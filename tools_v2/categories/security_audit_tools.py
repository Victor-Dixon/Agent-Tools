#!/usr/bin/env python3
"""Security audit tools for headers, external assets, and exposed endpoints."""

from __future__ import annotations

import logging
import socket
import time
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin, urlparse
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec

logger = logging.getLogger(__name__)


DEFAULT_TRUSTED_CDNS = {"cdnjs.cloudflare.com", "cdn.jsdelivr.net", "ajax.googleapis.com", "fonts.googleapis.com", "fonts.gstatic.com", "unpkg.com"}
DEFAULT_API_PATHS = ["/api", "/api/v1", "/api/v2", "/graphql", "/swagger", "/swagger/index.html", "/openapi.json"]
DEFAULT_DEBUG_PATHS = ["/debug", "/debug/vars", "/status", "/health", "/actuator", "/admin", "/__debug"]

DEFAULT_PORTS = [80, 443, 3000, 5000, 8000, 8080, 8443]
DEFAULT_SUBDOMAINS = ["www", "api", "dev", "staging", "test", "admin"]
COMMON_PUBLIC_SUFFIX_2 = {"co.uk", "org.uk", "ac.uk", "gov.uk", "com.au", "net.au", "org.au", "co.nz", "org.nz"}
COMMON_HOST_PREFIXES = {"www", "m", "app", "beta"}


def _apex_domain(host: str) -> str:
    host = (host or "").strip(".").lower()
    if not host:
        return host
    parts = host.split(".")
    if len(parts) <= 2:
        return host
    if parts[0] in COMMON_HOST_PREFIXES:
        parts = parts[1:]
    if len(parts) <= 2:
        return ".".join(parts)
    suffix2 = ".".join(parts[-2:])
    if suffix2 in COMMON_PUBLIC_SUFFIX_2 and len(parts) >= 3:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def _fetch_status(url: str, timeout: float, user_agent: str) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": user_agent})
    try:
        with urlopen(request, timeout=timeout) as resp:
            return {"status": int(resp.status), "retry_after": resp.headers.get("Retry-After")}
    except HTTPError as exc:
        try:
            return {
                "status": int(getattr(exc, "code", 0) or 0),
                "retry_after": exc.headers.get("Retry-After"),
            }
        except Exception:
            return {"status": int(getattr(exc, "code", 0) or 0)}
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:120]}
@dataclass
class ExternalResource:
    url: str
    has_integrity: bool


class ResourceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.resources: list[ExternalResource] = []
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k.lower(): v for k, v in attrs}
        if tag.lower() == "script" and attr_map.get("src"):
            self.resources.append(
                ExternalResource(
                    url=attr_map["src"],
                    has_integrity=bool(attr_map.get("integrity")),
                )
            )
        if tag.lower() == "link" and attr_map.get("href"):
            rel = (attr_map.get("rel") or "").lower()
            if "stylesheet" in rel:
                self.resources.append(
                    ExternalResource(
                        url=attr_map["href"],
                        has_integrity=bool(attr_map.get("integrity")),
                    )
                )


class SecurityAuditTool(IToolAdapter):
    """Audit web security headers, external assets, and exposed endpoints."""
    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="security.audit",
            version="1.0.0",
            category="compliance",
            summary="Audit security headers, external assets, and exposed endpoints for a URL",
            required_params=["url"],
            optional_params={
                "timeout": 10,
                "allow_redirects": True,
                "trusted_cdns": sorted(DEFAULT_TRUSTED_CDNS),
                "rate_limit_probe": False,
                "probe_requests": 5,
                "probe_delay": 0.25,
                "rate_limit_retest": False,
                "retest_delay": 1.0,
                "endpoint_paths": DEFAULT_API_PATHS,
                "debug_paths": DEFAULT_DEBUG_PATHS,
                "enable_premium": False,
                "ports": DEFAULT_PORTS,
                "subdomain_probe": False,
                "subdomains": DEFAULT_SUBDOMAINS,
            },
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        try:
            url = params["url"]
            timeout = float(params.get("timeout", 10))
            allow_redirects = bool(params.get("allow_redirects", True))
            trusted_cdns = set(params.get("trusted_cdns") or DEFAULT_TRUSTED_CDNS)
            endpoint_paths = params.get("endpoint_paths") or DEFAULT_API_PATHS
            debug_paths = params.get("debug_paths") or DEFAULT_DEBUG_PATHS
            rate_limit_probe = bool(params.get("rate_limit_probe", False))
            probe_requests = int(params.get("probe_requests", 5))
            probe_delay = float(params.get("probe_delay", 0.25))
            rate_limit_retest = bool(params.get("rate_limit_retest", False))
            retest_delay = float(params.get("retest_delay", 1.0))
            enable_premium = bool(params.get("enable_premium", False))
            ports = params.get("ports") or DEFAULT_PORTS
            subdomain_probe = bool(params.get("subdomain_probe", False))
            subdomains = params.get("subdomains") or DEFAULT_SUBDOMAINS

            response = self._fetch(url, timeout, allow_redirects)
            headers = {k.lower(): v for k, v in response.headers.items()}
            body = response.body
            base = response.final_url
            base_host = urlparse(base).hostname or ""

            header_results = self._check_security_headers(headers)
            sri_results, cdn_results = self._analyze_resources(body, base, base_host, trusted_cdns)
            rate_results = self._check_rate_limits(
                headers,
                url,
                timeout,
                rate_limit_probe,
                probe_requests,
                probe_delay,
                rate_limit_retest,
                retest_delay,
            )
            backend_info = self._extract_backend_info(headers)
            api_endpoints = self._probe_paths(base, endpoint_paths, timeout)
            debug_endpoints = self._probe_paths(base, debug_paths, timeout)
            port_scan = self._scan_ports(base_host, ports, timeout) if enable_premium else {
                "status": "premium_required",
                "ports_checked": ports,
                "open_ports": [],
            }
            subdomain_results = (
                self._probe_subdomains(base_host, subdomains)
                if subdomain_probe and base_host
                else {"status": "disabled", "subdomains": []}
            )

            score, findings = self._score_findings(
                header_results,
                sri_results,
                cdn_results,
                rate_results,
                backend_info,
                debug_endpoints,
            )

            output = {
                "target": base,
                "score": score,
                "findings": findings,
                "headers": header_results,
                "missing_sri": sri_results,
                "untrusted_cdn": cdn_results,
                "rate_limiting": rate_results,
                "backend_info": backend_info,
                "api_endpoints": api_endpoints,
                "debug_endpoints": debug_endpoints,
                "port_details": port_scan,
                "subdomain_enumeration": subdomain_results,
            }
            return ToolResult(success=True, output=output)
        except Exception as exc:
            logger.error(f"Security audit failed: {exc}")
            return ToolResult(success=False, output=None, error_message=str(exc), exit_code=1)
    def _fetch(self, url: str, timeout: float, allow_redirects: bool) -> "FetchResult":
        request = Request(
            url,
            headers={
                "User-Agent": "AgentTools-SecurityAudit/1.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        with urlopen(request, timeout=timeout) as resp:
            final_url = resp.geturl()
            if not allow_redirects and final_url != url:
                raise ValueError("Redirect detected but allow_redirects is false")
            body = resp.read(1_000_000)
            return FetchResult(headers=resp.headers, body=body, final_url=final_url)

    def _check_security_headers(self, headers: dict[str, str]) -> dict[str, Any]:
        required = [
            "content-security-policy",
            "x-frame-options",
            "x-content-type-options",
            "strict-transport-security",
            "referrer-policy",
            "permissions-policy",
            "access-control-allow-origin",
        ]
        result = {}
        for header in required:
            value = headers.get(header)
            result[header] = {
                "present": bool(value),
                "value": value,
                "wildcard": header == "access-control-allow-origin" and value == "*",
            }
        return result
    def _analyze_resources(
        self,
        body: bytes,
        base_url: str,
        base_host: str,
        trusted_cdns: set[str],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        parser = ResourceParser()
        content = body.decode("utf-8", errors="ignore")
        parser.feed(content)
        missing_sri = []
        untrusted_cdns = []
        for resource in parser.resources:
            absolute = urljoin(base_url, resource.url)
            parsed = urlparse(absolute)
            host = parsed.hostname or ""
            is_external = host and host != base_host
            if is_external and not resource.has_integrity:
                missing_sri.append(absolute)
            if is_external and host not in trusted_cdns:
                untrusted_cdns.append(absolute)
        return (
            {
                "missing_count": len(missing_sri),
                "missing_resources": missing_sri[:20],
            },
            {
                "untrusted_count": len(untrusted_cdns),
                "untrusted_resources": untrusted_cdns[:20],
            },
        )
    def _check_rate_limits(
        self,
        headers: dict[str, str],
        url: str,
        timeout: float,
        rate_limit_probe: bool,
        probe_requests: int,
        probe_delay: float,
        rate_limit_retest: bool,
        retest_delay: float,
    ) -> dict[str, Any]:
        header_keys = [
            "ratelimit-limit",
            "ratelimit-remaining",
            "x-ratelimit-limit",
            "x-ratelimit-remaining",
            "retry-after",
        ]
        header_present = {k: headers.get(k) for k in header_keys if headers.get(k)}
        probe_results = []
        if rate_limit_probe:
            for _ in range(max(probe_requests, 1)):
                result = self._probe_rate_limit(url, timeout)
                probe_results.append(result)
                time.sleep(max(probe_delay, 0))
            if rate_limit_retest:
                time.sleep(max(retest_delay, 0))
                for _ in range(max(probe_requests, 1)):
                    result = self._probe_rate_limit(url, timeout)
                    probe_results.append({**result, "retest": True})
                    time.sleep(max(probe_delay, 0))
        rate_limited = any(r["status"] == 429 for r in probe_results)
        return {
            "headers_detected": header_present,
            "rate_limit_headers": bool(header_present),
            "probe_enabled": rate_limit_probe,
            "retest_enabled": rate_limit_retest,
            "probe_results": probe_results,
            "rate_limit_triggered": rate_limited,
        }
    def _probe_rate_limit(self, url: str, timeout: float) -> dict[str, Any]:
        return _fetch_status(url, timeout, "AgentTools-RateProbe/1.0")

    def _extract_backend_info(self, headers: dict[str, str]) -> dict[str, Any]:
        keys = ["server", "x-powered-by", "via"]
        info = {k: headers.get(k) for k in keys if headers.get(k)}
        return {
            "exposed": bool(info),
            "details": info,
        }

    def _probe_paths(self, base_url: str, paths: list[str], timeout: float) -> list[dict[str, Any]]:
        results = []
        for path in paths:
            url = urljoin(base_url, path)
            result = _fetch_status(url, timeout, "AgentTools-EndpointProbe/1.0")
            if result.get("status") not in (404, "error"):
                results.append({"path": path, "url": url, **result})
        return [r for r in results if r.get("status") not in (404, "error")]

    def _scan_ports(self, host: str, ports: list[int], timeout: float) -> dict[str, Any]:
        service_map = {80: "http", 443: "https", 3000: "http-alt", 5000: "http-alt", 8000: "http-alt", 8080: "http-alt", 8443: "https-alt"}
        open_ports = []
        for port in ports:
            try:
                with socket.create_connection((host, int(port)), timeout=timeout):
                    open_ports.append({"port": port, "service": service_map.get(int(port), "unknown")})
            except Exception:
                continue
        return {
            "status": "completed",
            "ports_checked": ports,
            "open_ports": open_ports,
        }
    def _probe_subdomains(self, host: str, subdomains: list[str]) -> dict[str, Any]:
        apex = _apex_domain(host)
        results = []
        for sub in subdomains:
            fqdn = f"{sub}.{apex}" if apex else f"{sub}.{host}"
            try:
                socket.gethostbyname(fqdn)
                results.append({"subdomain": fqdn, "resolved": True})
            except Exception:
                continue
        return {"status": "completed", "subdomains": results}

    def _score_findings(
        self,
        header_results: dict[str, Any],
        sri_results: dict[str, Any],
        cdn_results: dict[str, Any],
        rate_results: dict[str, Any],
        backend_info: dict[str, Any],
        debug_endpoints: list[dict[str, Any]],
    ) -> tuple[int, list[str]]:
        score = 100
        findings = []
        for header, data in header_results.items():
            if header.lower() == "access-control-allow-origin":
                if data.get("present") and data.get("wildcard"):
                    score -= 10
                    findings.append("CORS wildcard '*' allows any origin")
                continue
            if not data["present"]:
                score -= 5
                findings.append(f"Missing {header} header")
        if sri_results["missing_count"]:
            score -= 5
            findings.append("Missing Subresource Integrity on external assets")
        if cdn_results["untrusted_count"]:
            score -= 5
            findings.append("Untrusted CDN resources detected")
        if not rate_results["rate_limit_headers"]:
            score -= 5
            findings.append("No rate limiting headers detected")
        if backend_info["exposed"]:
            score -= 5
            findings.append("Server information exposed in headers")
        if debug_endpoints:
            score -= 5
            findings.append("Debug endpoints detected")
        return max(score, 0), findings


@dataclass
class FetchResult:
    headers: Any
    body: bytes
    final_url: str


__all__ = ["SecurityAuditTool"]

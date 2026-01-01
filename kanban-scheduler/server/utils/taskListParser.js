/**
 * Parser for Master Task List markdown files
 * Extracts tasks, categories, priorities, and phases from markdown format
 */

function parseMasterTaskList(markdown) {
  const lines = markdown.split('\n');
  const result = {
    name: '',
    description: '',
    projects: [],
    categories: [],
    metadata: {}
  };

  let currentProject = null;
  let currentCategory = null;
  let inProjectSection = false;
  let inCategorySection = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    // Skip empty lines
    if (!line) continue;

    // Extract title (first # heading)
    if (line.startsWith('# ') && !result.name) {
      result.name = line.substring(2).trim();
      continue;
    }

    // Extract metadata
    if (line.startsWith('**Created:**') || line.startsWith('**Last Updated:**')) {
      result.metadata.created = line.split(':')[1]?.trim();
    }
    if (line.startsWith('**Status:**')) {
      result.metadata.status = line.split(':')[1]?.trim();
    }
    if (line.startsWith('**Goal:**')) {
      result.description = line.split(':')[1]?.trim();
    }

    // Detect project sections (## with emoji or bold)
    if (line.match(/^##\s+[🎮🖥️🔒📔🐺🎯]/) || line.match(/^##\s+\*\*/)) {
      const projectName = line.replace(/^##\s+/, '').replace(/[🎮🖥️🔒📔🐺🎯]/g, '').replace(/\*\*/g, '').trim();
      currentProject = {
        name: projectName,
        categories: []
      };
      result.projects.push(currentProject);
      inProjectSection = true;
      inCategorySection = false;
      continue;
    }

    // Detect category sections (###)
    if (line.startsWith('### ')) {
      const categoryName = line.substring(4).trim();
      currentCategory = {
        name: categoryName,
        tasks: []
      };
      
      if (currentProject) {
        currentProject.categories.push(currentCategory);
      } else {
        result.categories.push(currentCategory);
      }
      
      inCategorySection = true;
      continue;
    }

    // Detect priority sections (#### Phase 0A, etc.)
    if (line.match(/^####\s+Phase\s+0?[A-Z0-9]/i)) {
      const phaseMatch = line.match(/Phase\s+(0?[A-Z0-9])/i);
      if (phaseMatch && currentCategory) {
        currentCategory.phase = phaseMatch[1].toUpperCase();
      }
      continue;
    }

    // Parse task items (- [ ] or - [x])
    if (line.match(/^-\s+\[([ xX])\]/)) {
      const isCompleted = line.match(/\[([xX])\]/);
      const taskText = line.replace(/^-\s+\[[ xX]\]\s*/, '').trim();
      
      if (!taskText) continue;

      // Extract priority from tags like [P0], [P1], [HIGH], etc.
      let priority = 'MEDIUM';
      const priorityMatch = taskText.match(/\[(P[012]|HIGH|URGENT|LOW|MEDIUM)\]/i);
      if (priorityMatch) {
        const p = priorityMatch[1].toUpperCase();
        if (p.startsWith('P')) {
          priority = p === 'P0' ? 'URGENT' : p === 'P1' ? 'HIGH' : 'MEDIUM';
        } else {
          priority = p;
        }
      }

      // Extract category from tags like [CODE], [DOCS], etc.
      let category = currentCategory?.name || 'General';
      const categoryMatch = taskText.match(/\[(CODE|DOCS|QA|SEC|PERF|UX|INFRA|CLI|INTEG|FEAT|UI|TOOLS|ORG|CONSOLIDATE|CLEAN|PKG|BRAND|MCP)\]/i);
      if (categoryMatch) {
        const catMap = {
          'CODE': 'Code Quality',
          'DOCS': 'Documentation',
          'QA': 'Testing',
          'SEC': 'Security',
          'PERF': 'Performance',
          'UX': 'User Experience',
          'INFRA': 'Deployment',
          'CLI': 'Code Quality',
          'INTEG': 'Testing',
          'FEAT': 'Code Quality',
          'UI': 'User Experience',
          'TOOLS': 'Code Quality',
          'ORG': 'Code Quality',
          'CONSOLIDATE': 'Code Quality',
          'CLEAN': 'Code Quality',
          'PKG': 'Deployment',
          'BRAND': 'Documentation',
          'MCP': 'Code Quality'
        };
        category = catMap[categoryMatch[1].toUpperCase()] || category;
      }

      // Extract phase from context or tags
      let phase = currentCategory?.phase || '0A';
      const phaseMatch = taskText.match(/Phase\s+(0?[A-Z0-9])/i);
      if (phaseMatch) {
        phase = phaseMatch[1].toUpperCase();
      }

      // Clean task title (remove tags)
      const cleanTitle = taskText
        .replace(/\[[^\]]+\]/g, '') // Remove all tags
        .replace(/\s+/g, ' ')
        .trim();

      const task = {
        title: cleanTitle,
        status: isCompleted ? 'DONE' : 'TODO',
        priority: priority,
        category: category,
        phase: phase,
        description: `From ${currentProject?.name || 'Master Task List'}: ${category}`
      };

      if (currentCategory) {
        currentCategory.tasks.push(task);
      } else if (currentProject && currentProject.categories.length > 0) {
        // Add to last category of current project
        const lastCategory = currentProject.categories[currentProject.categories.length - 1];
        lastCategory.tasks.push(task);
      } else {
        // Add to root categories
        if (!result.categories.find(c => c.name === category)) {
          result.categories.push({ name: category, tasks: [] });
        }
        result.categories.find(c => c.name === category).tasks.push(task);
      }
    }
  }

  return result;
}

function flattenToTemplate(parsed) {
  // Convert parsed structure to template format for API
  const categories = [];

  // Add project-specific categories
  for (const project of parsed.projects || []) {
    for (const category of project.categories || []) {
      categories.push({
        name: `${project.name} - ${category.name}`,
        phase: category.phase || '0A',
        tasks: category.tasks.map(t => ({
          title: t.title,
          description: t.description,
          priority: t.priority
        }))
      });
    }
  }

  // Add root categories
  for (const category of parsed.categories || []) {
    categories.push({
      name: category.name,
      phase: category.phase || '0A',
      tasks: category.tasks.map(t => ({
        title: t.title,
        description: t.description,
        priority: t.priority
      }))
    });
  }

  return {
    name: parsed.name || 'Imported Master Task List',
    defaultPhase: '0A',
    categories: categories
  };
}

module.exports = {
  parseMasterTaskList,
  flattenToTemplate
};



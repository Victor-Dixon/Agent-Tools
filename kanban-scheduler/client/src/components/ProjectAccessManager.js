import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { projectSharingAPI } from '../services/api';
import toast from 'react-hot-toast';
import { UserPlusIcon, CheckIcon, XMarkIcon, UserMinusIcon } from '@heroicons/react/24/outline';
import RequestAccessModal from './RequestAccessModal';

const ProjectAccessManager = ({ projectId, projectName, ownerUsername, isOwner }) => {
  const [showRequestModal, setShowRequestModal] = useState(false);
  const queryClient = useQueryClient();

  const { data: membersData, isLoading } = useQuery(
    ['project-members', projectId],
    () => projectSharingAPI.getProjectMembers(projectId).then(res => res.data),
    { enabled: !!projectId }
  );

  const { data: requestsData } = useQuery(
    ['my-requests'],
    () => projectSharingAPI.getMyRequests().then(res => res.data),
    { enabled: !isOwner }
  );

  const { data: invitationsData } = useQuery(
    ['pending-invitations'],
    () => projectSharingAPI.getPendingInvitations().then(res => res.data),
    { enabled: isOwner }
  );

  const respondMutation = useMutation(
    ({ invitationId, action }) => projectSharingAPI.respondToInvitation(invitationId, action),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['pending-invitations']);
        queryClient.invalidateQueries(['project-members', projectId]);
        queryClient.invalidateQueries(['projects']);
        toast.success('Invitation responded successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to respond to invitation');
      }
    }
  );

  const removeMemberMutation = useMutation(
    ({ projectId, userId }) => projectSharingAPI.removeMember(projectId, userId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['project-members', projectId]);
        toast.success('Member removed successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to remove member');
      }
    }
  );

  const cancelRequestMutation = useMutation(
    (invitationId) => projectSharingAPI.cancelRequest(invitationId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['my-requests']);
        toast.success('Request cancelled');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to cancel request');
      }
    }
  );

  // Check if user already requested access
  const hasPendingRequest = requestsData?.requests?.some(
    req => req.project?.id === projectId && req.status === 'PENDING'
  );

  // Get pending invitations for this project
  const pendingInvitations = invitationsData?.invitations?.filter(
    inv => inv.project?.id === projectId
  ) || [];

  const members = membersData?.members || [];

  if (isLoading) {
    return <div className="text-sm text-gray-500">Loading...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">Access & Members</h3>
        {!isOwner && !hasPendingRequest && (
          <button
            onClick={() => setShowRequestModal(true)}
            className="btn-primary flex items-center gap-2 text-sm"
          >
            <UserPlusIcon className="h-4 w-4" />
            Request Access
          </button>
        )}
        {!isOwner && hasPendingRequest && (
          <span className="text-sm text-gray-500">Request pending...</span>
        )}
      </div>

      {/* Pending Invitations (Owner view) */}
      {isOwner && pendingInvitations.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 space-y-3">
          <h4 className="font-medium text-yellow-900">Pending Requests</h4>
          {pendingInvitations.map((invitation) => (
            <div key={invitation.id} className="flex items-center justify-between bg-white p-3 rounded">
              <div>
                <p className="font-medium text-gray-900">
                  {invitation.user.name || invitation.user.username}
                </p>
                <p className="text-sm text-gray-500">@{invitation.user.username}</p>
                {invitation.message && (
                  <p className="text-sm text-gray-600 mt-1">{invitation.message}</p>
                )}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => respondMutation.mutate({ invitationId: invitation.id, action: 'ACCEPT' })}
                  className="p-2 text-green-600 hover:bg-green-50 rounded"
                  title="Accept"
                >
                  <CheckIcon className="h-5 w-5" />
                </button>
                <button
                  onClick={() => respondMutation.mutate({ invitationId: invitation.id, action: 'REJECT' })}
                  className="p-2 text-red-600 hover:bg-red-50 rounded"
                  title="Reject"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Members List */}
      <div className="space-y-2">
        <h4 className="font-medium text-gray-900">Members ({members.length})</h4>
        {members.map((member) => (
          <div
            key={member.id || member.userId}
            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                <span className="text-primary-600 font-medium text-sm">
                  {(member.user.name || member.user.username || 'U').charAt(0).toUpperCase()}
                </span>
              </div>
              <div>
                <p className="font-medium text-gray-900">
                  {member.user.name || member.user.username}
                  {member.role === 'OWNER' && <span className="ml-2 text-xs text-gray-500">(Owner)</span>}
                </p>
                <p className="text-sm text-gray-500">@{member.user.username}</p>
              </div>
            </div>
            {isOwner && member.role !== 'OWNER' && (
              <button
                onClick={() => removeMemberMutation.mutate({ projectId, userId: member.userId })}
                className="p-2 text-red-600 hover:bg-red-50 rounded"
                title="Remove member"
              >
                <UserMinusIcon className="h-5 w-5" />
              </button>
            )}
          </div>
        ))}
      </div>

      <RequestAccessModal
        isOpen={showRequestModal}
        onClose={() => setShowRequestModal(false)}
        projectId={projectId}
        projectName={projectName}
        ownerUsername={ownerUsername}
      />
    </div>
  );
};

export default ProjectAccessManager;


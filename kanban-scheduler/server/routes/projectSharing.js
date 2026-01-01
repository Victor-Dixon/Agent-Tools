const express = require('express');
const { body, validationResult, query } = require('express-validator');
const prisma = require('../utils/database');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// Request access to a project by project ID (when you know the project owner's username)
router.post('/request/:projectId', authenticateToken, [
  body('message').optional().trim().isLength({ max: 500 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { projectId } = req.params;
    const { message } = req.body;
    const requesterId = req.user.id;

    // Find the project
    const project = await prisma.project.findUnique({
      where: { id: projectId },
      include: { user: true }
    });

    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }

    // Can't request access to your own project
    if (project.userId === requesterId) {
      return res.status(400).json({ error: 'You already own this project' });
    }

    // Check if user is already a member
    const existingMember = await prisma.projectMember.findUnique({
      where: {
        userId_projectId: {
          userId: requesterId,
          projectId: projectId
        }
      }
    });

    if (existingMember) {
      return res.status(400).json({ error: 'You are already a member of this project' });
    }

    // Check if there's already a pending invitation
    const existingInvitation = await prisma.projectInvitation.findUnique({
      where: {
        userId_projectId: {
          userId: requesterId,
          projectId: projectId
        }
      }
    });

    if (existingInvitation) {
      if (existingInvitation.status === 'PENDING') {
        return res.status(400).json({ error: 'You already have a pending request for this project' });
      } else if (existingInvitation.status === 'ACCEPTED') {
        // Create member if invitation was accepted but member doesn't exist
        await prisma.projectMember.create({
          data: {
            userId: requesterId,
            projectId: projectId,
            role: 'MEMBER'
          }
        });
        return res.json({ message: 'Access granted' });
      }
    }

    // Create new invitation request
    const invitation = await prisma.projectInvitation.create({
      data: {
        userId: requesterId,
        projectId: projectId,
        status: 'PENDING',
        message: message || null
      },
      include: {
        user: {
          select: {
            id: true,
            username: true,
            name: true,
            email: true
          }
        },
        project: {
          select: {
            id: true,
            name: true,
            user: {
              select: {
                id: true,
                username: true,
                name: true
              }
            }
          }
        }
      }
    });

    res.status(201).json({
      message: 'Access request sent successfully',
      invitation
    });
  } catch (error) {
    console.error('Request project access error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Request access by owner's username and project name
router.post('/request-by-username', authenticateToken, [
  body('ownerUsername').trim().isLength({ min: 1 }),
  body('projectName').trim().isLength({ min: 1 }),
  body('message').optional().trim().isLength({ max: 500 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { ownerUsername, projectName, message } = req.body;
    const requesterId = req.user.id;

    // Find the owner by username
    const owner = await prisma.user.findUnique({
      where: { username: ownerUsername }
    });

    if (!owner) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Find the project
    const project = await prisma.project.findFirst({
      where: {
        userId: owner.id,
        name: projectName
      }
    });

    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }

    // Can't request access to your own project
    if (project.userId === requesterId) {
      return res.status(400).json({ error: 'You already own this project' });
    }

    // Check if user is already a member
    const existingMember = await prisma.projectMember.findUnique({
      where: {
        userId_projectId: {
          userId: requesterId,
          projectId: project.id
        }
      }
    });

    if (existingMember) {
      return res.status(400).json({ error: 'You are already a member of this project' });
    }

    // Check if there's already a pending invitation
    const existingInvitation = await prisma.projectInvitation.findUnique({
      where: {
        userId_projectId: {
          userId: requesterId,
          projectId: project.id
        }
      }
    });

    if (existingInvitation) {
      if (existingInvitation.status === 'PENDING') {
        return res.status(400).json({ error: 'You already have a pending request for this project' });
      }
    }

    // Create new invitation request
    const invitation = await prisma.projectInvitation.create({
      data: {
        userId: requesterId,
        projectId: project.id,
        status: 'PENDING',
        message: message || null
      },
      include: {
        user: {
          select: {
            id: true,
            username: true,
            name: true,
            email: true
          }
        },
        project: {
          select: {
            id: true,
            name: true,
            user: {
              select: {
                id: true,
                username: true,
                name: true
              }
            }
          }
        }
      }
    });

    res.status(201).json({
      message: 'Access request sent successfully',
      invitation
    });
  } catch (error) {
    console.error('Request project access by username error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get pending invitations for projects I own
router.get('/pending-invitations', authenticateToken, async (req, res) => {
  try {
    const invitations = await prisma.projectInvitation.findMany({
      where: {
        project: {
          userId: req.user.id
        },
        status: 'PENDING'
      },
      include: {
        user: {
          select: {
            id: true,
            username: true,
            name: true,
            email: true
          }
        },
        project: {
          select: {
            id: true,
            name: true,
            description: true
          }
        }
      },
      orderBy: {
        createdAt: 'desc'
      }
    });

    res.json({ invitations });
  } catch (error) {
    console.error('Get pending invitations error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get my pending requests (requests I've sent)
router.get('/my-requests', authenticateToken, async (req, res) => {
  try {
    const requests = await prisma.projectInvitation.findMany({
      where: {
        userId: req.user.id,
        status: 'PENDING'
      },
      include: {
        project: {
          select: {
            id: true,
            name: true,
            description: true,
            user: {
              select: {
                id: true,
                username: true,
                name: true
              }
            }
          }
        }
      },
      orderBy: {
        createdAt: 'desc'
      }
    });

    res.json({ requests });
  } catch (error) {
    console.error('Get my requests error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Accept or reject an invitation (project owner)
router.put('/invitation/:invitationId/respond', authenticateToken, [
  body('action').isIn(['ACCEPT', 'REJECT'])
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { invitationId } = req.params;
    const { action } = req.body;

    // Find the invitation
    const invitation = await prisma.projectInvitation.findUnique({
      where: { id: invitationId },
      include: {
        project: true
      }
    });

    if (!invitation) {
      return res.status(404).json({ error: 'Invitation not found' });
    }

    // Verify the user owns the project
    if (invitation.project.userId !== req.user.id) {
      return res.status(403).json({ error: 'You do not have permission to respond to this invitation' });
    }

    if (invitation.status !== 'PENDING') {
      return res.status(400).json({ error: 'This invitation has already been responded to' });
    }

    const newStatus = action === 'ACCEPT' ? 'ACCEPTED' : 'REJECTED';

    // Update invitation status
    await prisma.projectInvitation.update({
      where: { id: invitationId },
      data: { status: newStatus }
    });

    // If accepted, create project member
    if (action === 'ACCEPT') {
      await prisma.projectMember.create({
        data: {
          userId: invitation.userId,
          projectId: invitation.projectId,
          role: 'MEMBER'
        }
      });
    }

    res.json({
      message: `Invitation ${action === 'ACCEPT' ? 'accepted' : 'rejected'} successfully`
    });
  } catch (error) {
    console.error('Respond to invitation error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get project members
router.get('/project/:projectId/members', authenticateToken, async (req, res) => {
  try {
    const { projectId } = req.params;

    // Check if user has access to the project
    const project = await prisma.project.findUnique({
      where: { id: projectId },
      include: {
        members: {
          include: {
            user: {
              select: {
                id: true,
                username: true,
                name: true,
                email: true,
                avatar: true
              }
            }
          }
        }
      }
    });

    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }

    // Check if user is owner or member
    const isOwner = project.userId === req.user.id;
    const isMember = project.members.some(m => m.userId === req.user.id);

    if (!isOwner && !isMember) {
      return res.status(403).json({ error: 'You do not have access to this project' });
    }

    // Add owner to members list
    const owner = await prisma.user.findUnique({
      where: { id: project.userId },
      select: {
        id: true,
        username: true,
        name: true,
        email: true,
        avatar: true
      }
    });

    const allMembers = [
      {
        id: 'owner-' + owner.id,
        userId: owner.id,
        role: 'OWNER',
        createdAt: project.createdAt,
        user: owner
      },
      ...project.members.map(m => ({
        ...m,
        role: m.role
      }))
    ];

    res.json({ members: allMembers });
  } catch (error) {
    console.error('Get project members error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Remove a member from a project (owner/admin only)
router.delete('/project/:projectId/members/:userId', authenticateToken, async (req, res) => {
  try {
    const { projectId, userId } = req.params;

    const project = await prisma.project.findUnique({
      where: { id: projectId }
    });

    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }

    // Only owner can remove members
    if (project.userId !== req.user.id) {
      return res.status(403).json({ error: 'Only the project owner can remove members' });
    }

    // Can't remove yourself
    if (userId === req.user.id) {
      return res.status(400).json({ error: 'You cannot remove yourself from the project' });
    }

    await prisma.projectMember.deleteMany({
      where: {
        projectId: projectId,
        userId: userId
      }
    });

    res.json({ message: 'Member removed successfully' });
  } catch (error) {
    console.error('Remove member error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Cancel a request (the requester cancels their own request)
router.delete('/request/:invitationId', authenticateToken, async (req, res) => {
  try {
    const { invitationId } = req.params;

    const invitation = await prisma.projectInvitation.findUnique({
      where: { id: invitationId }
    });

    if (!invitation) {
      return res.status(404).json({ error: 'Request not found' });
    }

    // Only the requester can cancel their request
    if (invitation.userId !== req.user.id) {
      return res.status(403).json({ error: 'You can only cancel your own requests' });
    }

    await prisma.projectInvitation.update({
      where: { id: invitationId },
      data: { status: 'CANCELLED' }
    });

    res.json({ message: 'Request cancelled successfully' });
  } catch (error) {
    console.error('Cancel request error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;


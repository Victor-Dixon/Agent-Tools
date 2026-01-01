// Project Phases
export const PROJECT_PHASES = {
  '0A': {
    code: '0A',
    name: 'Organization and Planning',
    description: 'Initial planning, requirements gathering, and project organization',
    color: '#8B5CF6', // Purple
    icon: '📋'
  },
  '0B': {
    code: '0B',
    name: 'Research',
    description: 'Research phase, exploring options and gathering information',
    color: '#3B82F6', // Blue
    icon: '🔍'
  },
  '1': {
    code: '1',
    name: 'Design',
    description: 'Design phase, creating mockups and architecture',
    color: '#10B981', // Green
    icon: '🎨'
  },
  '2': {
    code: '2',
    name: 'Development',
    description: 'Active development and implementation',
    color: '#F59E0B', // Amber
    icon: '💻'
  },
  '3': {
    code: '3',
    name: 'Testing',
    description: 'Testing, QA, and bug fixes',
    color: '#EF4444', // Red
    icon: '🧪'
  },
  '4': {
    code: '4',
    name: 'Deployment',
    description: 'Deployment and release preparation',
    color: '#06B6D4', // Cyan
    icon: '🚀'
  },
  '5': {
    code: '5',
    name: 'Maintenance',
    description: 'Ongoing maintenance and updates',
    color: '#6B7280', // Gray
    icon: '🔧'
  }
};

export const getPhaseInfo = (phase) => {
  return PROJECT_PHASES[phase] || PROJECT_PHASES['0A'];
};

export const getPhaseColor = (phase) => {
  return getPhaseInfo(phase).color;
};

export const getPhaseName = (phase) => {
  return getPhaseInfo(phase).name;
};

export const PHASE_OPTIONS = Object.values(PROJECT_PHASES);



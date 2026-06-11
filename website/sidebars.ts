import type { SidebarsConfig } from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  docsSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting started',
      items: [
        'getting-started/quick-start',
        'getting-started/ide-and-workspaces',
        'getting-started/dev-container',
        'getting-started/ocp-viewer',
        'getting-started/project-layout',
        'getting-started/github-setup',
        'getting-started/releases',
      ],
    },
    {
      type: 'category',
      label: 'Modeling',
      items: [
        'modeling/conventions',
        'modeling/parts-and-assemblies',
        'modeling/testing',
        'modeling/external-libraries',
      ],
    },
    {
      type: 'category',
      label: 'Tools',
      items: [
        'tools/just',
        'tools/makerrepo',
        {
          type: 'category',
          label: 'CAD tooling',
          items: [
            'tools/cad-tooling/index',
            'tools/cad-tooling/export',
            'tools/cad-tooling/render',
            'tools/cad-tooling/release-notes',
          ],
        },
        'tools/mcp-servers',
        'tools/uv-and-quality',
      ],
    },
    {
      type: 'category',
      label: 'Workflows',
      items: [
        'workflows/daily-development',
        'workflows/visual-verification',
        'workflows/export-and-formats',
        'workflows/ci-and-dagger',
        'workflows/releases',
      ],
    },
    {
      type: 'category',
      label: 'Troubleshooting',
      items: [
        'troubleshooting/index',
        'troubleshooting/dev-container',
        'troubleshooting/ocp-viewer',
        'troubleshooting/mcp',
        'troubleshooting/dagger-and-docker',
        'troubleshooting/export-and-ci',
      ],
    },
    {
      type: 'category',
      label: 'Reference',
      items: [
        'reference/justfile-recipes',
        'reference/open-cascade',
        'reference/ci-functions',
        'reference/glossary',
      ],
    },
    {
      type: 'category',
      label: 'Contributing',
      items: ['contributing/for-humans', 'contributing/for-agents'],
    },
  ],
};

export default sidebars;

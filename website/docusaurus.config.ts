import { themes as prismThemes } from 'prism-react-renderer';
import type { Config } from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import { repoIdentity } from './repo-identity';

const config: Config = {
  title: repoIdentity.docsTitle,
  tagline: repoIdentity.tagline,

  url: repoIdentity.pagesUrl,
  baseUrl: repoIdentity.baseUrl,

  organizationName: repoIdentity.githubOwner,
  projectName: repoIdentity.githubRepo,

  onBrokenLinks: 'throw',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  markdown: {
    mermaid: true,
  },

  themes: ['@docusaurus/theme-mermaid'],

  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/',
          sidebarPath: './sidebars.ts',
          editUrl: `${repoIdentity.githubUrl}/tree/main/website/`,
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/repo_preview.png',
    navbar: {
      title: repoIdentity.navbarTitle,
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docsSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          href: repoIdentity.githubUrl,
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            { label: 'Quick start', to: '/getting-started/quick-start' },
            { label: 'Troubleshooting', to: '/troubleshooting/' },
          ],
        },
        {
          title: 'Repository',
          items: [
            {
              label: 'GitHub',
              href: repoIdentity.githubUrl,
            },
            {
              label: 'AGENTS.md',
              href: `${repoIdentity.githubUrl}/blob/main/AGENTS.md`,
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} ${repoIdentity.copyrightHolder}. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;

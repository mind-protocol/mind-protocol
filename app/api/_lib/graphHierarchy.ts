import { createClient, type RedisClientType } from 'redis';

interface CitizenEntry {
  slug: string;
  graph_id: string;
  name: string;
}

interface OrganizationEntry {
  slug: string;
  graph_id: string;
  name: string;
  citizens: CitizenEntry[];
}

export interface EcosystemEntry {
  slug: string;
  graph_id: string;
  name: string;
  organizations: OrganizationEntry[];
  citizens: CitizenEntry[];
}

interface GraphHierarchy {
  ecosystems: EcosystemEntry[];
}

const redisUrl = process.env.REDIS_URL || 'redis://127.0.0.1:6379';

let redisClient: RedisClientType | null = null;
let redisClientPromise: Promise<RedisClientType> | null = null;

async function getRedisClient(): Promise<RedisClientType> {
  if (redisClient) {
    return redisClient;
  }

  if (!redisClientPromise) {
    const client = createClient({ url: redisUrl });
    client.on('error', err => {
      console.error('[GraphHierarchy] Redis connection error:', err);
    });
    redisClientPromise = client.connect().then(instance => {
      redisClient = instance as RedisClientType;
      return instance as RedisClientType;
    }).catch(err => {
      redisClientPromise = null;
      throw err;
    });
  }

  return redisClientPromise;
}

const toString = (value: unknown): string =>
  typeof value === 'string' ? value : Buffer.isBuffer(value) ? value.toString('utf8') : String(value ?? '');

const toTitleCase = (value: string) =>
  value.replace(/[-_]/g, ' ').replace(/\b\w/g, char => char.toUpperCase());

function buildHierarchy(graphNames: string[]): GraphHierarchy {
  const ecosystemsMap = new Map<string, EcosystemEntry>();

  const ensureEcosystem = (slug: string): EcosystemEntry => {
    if (!ecosystemsMap.has(slug)) {
      ecosystemsMap.set(slug, {
        slug,
        graph_id: slug,
        name: toTitleCase(slug),
        organizations: [],
        citizens: []
      });
    }
    return ecosystemsMap.get(slug)!;
  };

  graphNames.forEach(name => {
    const graphName = toString(name);
    if (!graphName) {
      return;
    }

    const segments = graphName.split('_');
    if (segments.length === 1) {
      const ecosystem = ensureEcosystem(segments[0]);
      ecosystem.graph_id = graphName;
      ecosystem.name = toTitleCase(segments[0]);
      return;
    }

    const ecosystemSlug = segments[0];
    const ecosystem = ensureEcosystem(ecosystemSlug);

    if (segments.length === 2) {
      const organizationSlug = segments[1];

      const existingOrgIndex = ecosystem.organizations.findIndex(org => org.slug === organizationSlug);
      if (existingOrgIndex >= 0) {
        ecosystem.organizations[existingOrgIndex] = {
          ...ecosystem.organizations[existingOrgIndex],
          graph_id: graphName,
          name: toTitleCase(organizationSlug)
        };
      } else {
        ecosystem.organizations.push({
          slug: organizationSlug,
          graph_id: graphName,
          name: toTitleCase(organizationSlug),
          citizens: []
        });
      }
      return;
    }

    const organizationSlug = segments[1];
    const citizenSlug = segments.slice(2).join('_');

    let organization = ecosystem.organizations.find(org => org.slug === organizationSlug);
    if (!organization) {
      organization = {
        slug: organizationSlug,
        graph_id: `${ecosystemSlug}_${organizationSlug}`,
        name: toTitleCase(organizationSlug),
        citizens: []
      };
      ecosystem.organizations.push(organization);
    }

    const citizenEntry: CitizenEntry = {
      slug: citizenSlug,
      graph_id: graphName,
      name: toTitleCase(citizenSlug)
    };
    organization.citizens.push(citizenEntry);
    ecosystem.citizens.push(citizenEntry);
  });

  const sortCitizens = (citizens: CitizenEntry[]) =>
    citizens.sort((a, b) => a.slug.localeCompare(b.slug));

  const ecosystems = Array.from(ecosystemsMap.values())
    .map(ecosystem => ({
      ...ecosystem,
      organizations: ecosystem.organizations
        .map(org => ({
          ...org,
          citizens: sortCitizens(org.citizens)
        }))
        .sort((a, b) => a.slug.localeCompare(b.slug)),
      citizens: sortCitizens(ecosystem.citizens)
    }))
    .sort((a, b) => a.slug.localeCompare(b.slug));

  return { ecosystems };
}

export async function fetchGraphHierarchy(): Promise<GraphHierarchy> {
  const client = await getRedisClient();
  const rawGraphs = await client.sendCommand<string[]>(['GRAPH.LIST']);
  return buildHierarchy(rawGraphs || []);
}

export async function getEcosystemListing(slug: string): Promise<EcosystemEntry | null> {
  const hierarchy = await fetchGraphHierarchy();
  return hierarchy.ecosystems.find(eco => eco.slug === slug) || null;
}

export async function getOrganizationListing(ecosystemSlug: string, organizationSlug: string) {
  const ecosystem = await getEcosystemListing(ecosystemSlug);
  if (!ecosystem) {
    return null;
  }
  const organization = ecosystem.organizations.find(org => org.slug === organizationSlug) || null;
  return { ecosystem, organization };
}

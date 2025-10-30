import { NextRequest, NextResponse } from 'next/server';
import { getEcosystemListing, getOrganizationListing } from '../../_lib/graphHierarchy';

const BACKEND_BASE_URL = process.env.CONSCIOUSNESS_BACKEND_URL || 'http://localhost:8000';

type RouteContext = {
  params: Promise<{
    hierarchy: string[];
  }>;
};

const respondNotFound = (message: string) =>
  NextResponse.json({ error: message }, { status: 404 });

const respondBadRequest = (message: string) =>
  NextResponse.json({ error: message }, { status: 400 });

export async function GET(request: NextRequest, context: RouteContext) {
  const params = await context.params;
  const hierarchy = params?.hierarchy ?? [];
  const wantsGraphs = hierarchy.length > 0 && hierarchy[hierarchy.length - 1] === 'graphs';

  if (wantsGraphs) {
    const segments = hierarchy.slice(0, -1);

    try {
      if (segments.length === 1) {
        const ecosystemSlug = segments[0];
        const ecosystem = await getEcosystemListing(ecosystemSlug);
        if (!ecosystem) {
          return respondNotFound(`Ecosystem not found: ${ecosystemSlug}`);
        }

        return NextResponse.json({
          ecosystem: {
            slug: ecosystem.slug,
            graph_id: ecosystem.graph_id,
            name: ecosystem.name
          },
          organizations: ecosystem.organizations.map(org => ({
            slug: org.slug,
            graph_id: org.graph_id,
            name: org.name
          })),
          citizens: ecosystem.citizens
        });
      }

      if (segments.length === 3 && segments[1] === 'organization') {
        const ecosystemSlug = segments[0];
        const organizationSlug = segments[2];
        const listing = await getOrganizationListing(ecosystemSlug, organizationSlug);

        if (!listing || !listing.organization) {
          if (!listing || !listing.ecosystem) {
            return respondNotFound(`Ecosystem not found: ${ecosystemSlug}`);
          }
          return respondNotFound(`Organization not found: ${organizationSlug}`);
        }

        return NextResponse.json({
          ecosystem: {
            slug: listing.ecosystem.slug,
            graph_id: listing.ecosystem.graph_id,
            name: listing.ecosystem.name
          },
          organization: {
            slug: listing.organization.slug,
            graph_id: listing.organization.graph_id,
            name: listing.organization.name
          },
          citizens: listing.organization.citizens
        });
      }

      return respondBadRequest('Invalid hierarchy for graphs listing');
    } catch (error) {
      console.error('[HierarchyAPI] Redis hierarchy lookup failed, falling back to backend:', error);
      // fall through to backend proxy below
    }
  }

  const url = new URL(request.url);
  const backendPath = `${BACKEND_BASE_URL}${url.pathname}${url.search}`;

  try {
    const response = await fetch(backendPath, {
      method: 'GET',
      signal: AbortSignal.timeout(15000)
    });

    const bodyText = await response.text();
    const contentType = response.headers.get('content-type') || 'application/json';

    if (contentType.includes('application/json')) {
      try {
        const data = bodyText ? JSON.parse(bodyText) : {};
        return NextResponse.json(data, { status: response.status });
      } catch (err) {
        console.warn('[HierarchyAPI] Backend JSON parse failed, returning raw text:', err);
      }
    }

    return new NextResponse(bodyText, {
      status: response.status,
      headers: { 'Content-Type': contentType }
    });
  } catch (error) {
    console.error('[HierarchyAPI] Backend fetch failed:', error);
    return NextResponse.json(
      {
        error: 'Backend connection failed',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 503 }
    );
  }
}

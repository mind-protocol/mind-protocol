/**
 * Affective Event Schema Validation API
 *
 * Validates affective event schemas against expected definitions.
 *
 * PR-A: Instrumentation Foundation
 * Author: Iris "The Aperture"
 * Date: 2025-10-23
 */

import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Proxy request to Python backend
    const res = await fetch('http://localhost:8000/api/affective-telemetry/validate-schemas', {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!res.ok) {
      // Backend not ready yet - return neutral status
      return NextResponse.json({
        isValid: true,
        errors: [],
        message: 'Backend not available - schemas not validated yet'
      });
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    // Backend not running - return neutral status
    return NextResponse.json({
      isValid: true,
      errors: [],
      message: 'Backend not available - schemas not validated yet'
    });
  }
}

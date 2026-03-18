import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

// GET /api/citizens/[handle] — single citizen profile
export async function GET(
  _req: Request,
  { params }: { params: Promise<{ handle: string }> }
) {
  const { handle } = await params;
  const filePath = path.join(process.cwd(), 'public', 'data', 'citizens.json');
  const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  const citizen = data.find((c: { handle: string }) => c.handle === handle);

  if (!citizen) {
    return NextResponse.json({ error: 'Citizen not found' }, { status: 404 });
  }

  return NextResponse.json(citizen);
}

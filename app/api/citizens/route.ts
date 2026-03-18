import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

// GET /api/citizens — list all citizens
// Reads from public/data/citizens.json (generated from L3 profile.json files)
export async function GET() {
  const filePath = path.join(process.cwd(), 'public', 'data', 'citizens.json');
  const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  return NextResponse.json(data);
}

import type { Metadata } from "next";
import { Cinzel, Crimson_Text } from 'next/font/google';
import "./globals.css";
import { BrowserSignalsCollector } from "./consciousness/components/BrowserSignalsCollector";

// Venice/Serenissima Typography (from VENICE_DESIGN_SYSTEM_EXTRACT.md)
const cinzel = Cinzel({
  subsets: ['latin'],
  weight: ['400', '600', '700'],
  variable: '--font-cinzel',
  display: 'swap',
});

const crimsonText = Crimson_Text({
  subsets: ['latin'],
  weight: ['400', '600', '700'],
  style: ['normal', 'italic'],
  variable: '--font-crimson-text',
  display: 'swap',
});

export const metadata: Metadata = {
  title: "Mind Protocol - Consciousness Substrate",
  description: "Real-time consciousness substrate visualization and interaction",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning className={`${cinzel.variable} ${crimsonText.variable}`}>
      <body className="bg-parchment-base text-venice-brown antialiased font-crimson">
        <BrowserSignalsCollector />
        {children}
      </body>
    </html>
  );
}

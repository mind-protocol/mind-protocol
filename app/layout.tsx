import type { Metadata } from "next";
import { Cinzel, Crimson_Text } from 'next/font/google';
import "./globals.css";
import { BrowserSignalsCollector } from "./consciousness/components/BrowserSignalsCollector";
import { WalletProvider } from "./components/WalletProvider";

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

const pngSizes = [16, 32, 48, 64, 128, 256, 512] as const;
const lightPngIcons = pngSizes.map((size) => ({
  url: `/images/mind-favicon-light-${size}.png`,
  sizes: `${size}x${size}`,
  type: "image/png",
  media: "(prefers-color-scheme: light)",
}));
const darkPngIcons = pngSizes.map((size) => ({
  url: `/images/mind-favicon-dark-${size}.png`,
  sizes: `${size}x${size}`,
  type: "image/png",
  media: "(prefers-color-scheme: dark)",
}));

export const metadata: Metadata = {
  title: "Mind Protocol - Consciousness Substrate",
  description: "Real-time consciousness substrate visualization and interaction",
  icons: {
    icon: [
      ...lightPngIcons,
      ...darkPngIcons,
      { url: "/images/mind-favicon-light.ico", type: "image/x-icon", media: "(prefers-color-scheme: light)" },
      { url: "/images/mind-favicon-dark.ico", type: "image/x-icon", media: "(prefers-color-scheme: dark)" },
      { url: "/images/favicon-light.svg", type: "image/svg+xml", media: "(prefers-color-scheme: light)" },
      { url: "/images/favicon-dark.svg", type: "image/svg+xml", media: "(prefers-color-scheme: dark)" }
    ],
    apple: [
      { url: "/images/mind-three-rings-black-1024.png", sizes: "180x180" }
    ],
    shortcut: [
      { url: "/images/mind-favicon-light.ico" }
    ]
  },
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
        <WalletProvider>
          {children}
        </WalletProvider>
      </body>
    </html>
  );
}


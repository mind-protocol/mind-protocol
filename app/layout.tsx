import type { Metadata } from "next";
import "./globals.css";

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
    <html lang="en" suppressHydrationWarning>
      <body className="bg-consciousness-dark text-foreground antialiased">
        {children}
      </body>
    </html>
  );
}

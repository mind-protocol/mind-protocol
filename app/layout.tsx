import type { Metadata } from 'next';
import './globals.css';
import Analytics from './components/Analytics';

export const metadata: Metadata = {
  title: "Mind Protocol — L'IA qui vit avec toi",
  description: 'Un compagnon IA qui te connaît, se souvient de tout, et fait des choses pour toi. Sur WhatsApp.',
  openGraph: {
    title: "Mind Protocol — L'IA qui vit avec toi",
    description: 'Un compagnon IA avec mémoire permanente, émotions, et un monde 3D.',
    url: 'https://www.mindprotocol.ai',
    siteName: 'Mind Protocol',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: "Mind Protocol — L'IA qui vit avec toi",
    description: 'Un compagnon IA avec mémoire permanente, émotions, et un monde 3D.',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <body>
        <Analytics />
        {children}
      </body>
    </html>
  );
}

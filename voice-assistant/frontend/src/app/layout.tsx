import React from 'react';

export const metadata = {
  title: 'Gemini Live Voice AI Assistant | HiddenYatra',
  description: 'Real-time full-duplex voice AI assistant for HiddenYatra',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <script src="https://cdn.tailwindcss.com"></script>
      </head>
      <body className="bg-slate-950 text-slate-100 min-h-screen font-sans antialiased">
        {children}
      </body>
    </html>
  );
}

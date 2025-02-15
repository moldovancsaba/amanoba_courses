export const metadata = {
  title: "Simple Kanban CRM",
  description: "A simple and efficient Kanban-style CRM",
};

import "./globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-100">{children}</body>
    </html>
  );
}
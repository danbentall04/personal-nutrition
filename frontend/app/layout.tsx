// Wraps every page. Rails equivalent: app/views/layouts/application.html.erb,
// with `{children}` in place of `<%= yield %>`.
import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";

import "./globals.css";

export const metadata: Metadata = {
  title: "Personal Nutrition",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en-GB">
      <body>
        <header className="site-header">
          <span className="brand">Nutrition</span>
          <nav>
            <Link href="/">Dashboard</Link>
            <Link href="/profile">Profile</Link>
          </nav>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}

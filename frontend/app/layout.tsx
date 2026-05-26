import "./globals.css";
import type { Metadata } from "next";
import type { ReactNode } from "react";
import { ThemeProvider } from "@/components/theme-provider";

export const metadata: Metadata = {
  title: "End-of-Well Intelligence",
  description: "Cohere-powered drilling intelligence demo"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className="font-regular antialiased">
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}

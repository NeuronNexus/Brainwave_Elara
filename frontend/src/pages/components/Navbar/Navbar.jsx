import React, { useState } from 'react';
import { Menu, X, Box } from 'lucide-react';

// 1. Desktop Link Component
const DesktopLink = ({ href, children }) => (
  <a
    href={href}
    className="text-slate-300 hover:text-white hover:bg-slate-800 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200"
  >
    {children}
  </a>
);

// 2. Mobile Link Component
const MobileLink = ({ href, children }) => (
  <a
    href={href}
    className="text-slate-300 hover:text-white block px-3 py-2 rounded-md text-base font-medium"
  >
    {children}
  </a>
);

// --- Main Navbar Component ---
export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-900/80 backdrop-blur-md border-b border-slate-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo Area */}
          <div className="flex-shrink-0 flex items-center gap-2 cursor-pointer group">
            <div className="bg-indigo-500 p-1.5 rounded-lg group-hover:bg-indigo-400 transition-colors">
              <Box className="h-6 w-6 text-white" />
            </div>
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
              Project<span className="font-light"> IQ</span>
            </span>
          </div>

          {/* Desktop Menu - EDIT LINKS HERE */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-8">
              <DesktopLink href="/features">Features</DesktopLink>
              <DesktopLink href="/evaluate">Evaluate</DesktopLink>
              <DesktopLink href="/verify">Verify</DesktopLink>
              <DesktopLink href="/contact">Contact</DesktopLink>

              <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-full text-sm font-medium transition-all shadow-lg shadow-indigo-500/20">
                Get Started
              </button>
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="-mr-2 flex md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 focus:outline-none"
            >
              {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Panel - EDIT LINKS HERE */}
      {isOpen && (
        <div className="md:hidden bg-slate-900 border-b border-slate-700">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            
            <MobileLink href="/features">Features</MobileLink>
            <MobileLink href="/evaluate">Evaluate</MobileLink>
            <MobileLink href="/verify">Verify</MobileLink>
            <MobileLink href="/contact">Contact</MobileLink>

            <button className="w-full mt-4 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-base font-medium transition-colors">
              Get Started
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}
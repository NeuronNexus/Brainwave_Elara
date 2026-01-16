// --- Footer Component ---
import React from 'react';
import { 
  Github, 
  Twitter, 
  Linkedin,
  Box
} from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 pt-16 pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
          {/* Brand Column */}
          <div className="col-span-1 md:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <Box className="h-6 w-6 text-indigo-400" />
              <span className="text-xl font-bold text-white">ProjectIQ</span>
            </div>
            <p className="text-slate-400 text-sm leading-relaxed">
              Give your project a powerful identity, generate professional certificates in minutes using Artificial Intelligence.
            </p>
          </div>

          {/* Links Columns */}
          <div>
            <h3 className="text-sm font-semibold text-slate-200 tracking-wider uppercase mb-4">Product</h3>
            <ul className="space-y-3">
              {['Overview', 'Features', 'Solutions', 'Tutorials'].map((item) => (
                <li key={item}><a href="#" className="text-slate-400 hover:text-indigo-400 text-sm transition-colors">{item}</a></li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-200 tracking-wider uppercase mb-4">Company</h3>
            <ul className="space-y-3">
              {['About', 'Careers', 'Press', 'News'].map((item) => (
                <li key={item}><a href="#" className="text-slate-400 hover:text-indigo-400 text-sm transition-colors">{item}</a></li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-200 tracking-wider uppercase mb-4">Legal</h3>
            <ul className="space-y-3">
              {['Terms', 'Privacy', 'Cookies', 'Licenses'].map((item) => (
                <li key={item}><a href="#" className="text-slate-400 hover:text-indigo-400 text-sm transition-colors">{item}</a></li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-slate-500 text-sm">
            © {new Date().getFullYear()} ProjectIQ Inc. All rights reserved.
          </p>
          <div className="flex space-x-6">
            {[Github, Twitter, Linkedin].map((Icon, idx) => (
              <a key={idx} href="#" className="text-slate-400 hover:text-white transition-colors">
                <Icon className="h-5 w-5" />
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
};
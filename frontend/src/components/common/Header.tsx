'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import Icon from '@/components/ui/AppIcon';

interface NavigationItem {
  label: string;
  path: string;
  icon: string;
}

const navigationItems: NavigationItem[] = [
  {
    label: 'Daily Session',
    path: '/daily-session',
    icon: 'AcademicCapIcon',
  },
  {
    label: 'Progress',
    path: '/progress-dashboard',
    icon: 'ChartBarIcon',
  },
  {
    label: 'Question Bank',
    path: '/question-bank',
    icon: 'BookOpenIcon',
  },
  {
    label: 'Review',
    path: '/question-review',
    icon: 'DocumentTextIcon',
  },
  {
    label: 'Config',
    path: '/config',
    icon: 'Cog6ToothIcon',
  },
];

export default function Header() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActivePath = (path: string) => {
    return pathname === path;
  };

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-[100] bg-card shadow-md">
      <nav className="h-[60px] px-24 flex items-center justify-between">
        <Link 
          href="/daily-session" 
          className="flex items-center gap-12 transition-smooth hover:opacity-80"
          onClick={closeMobileMenu}
        >
          <div className="flex items-center gap-12">
            <svg
              width="40"
              height="40"
              viewBox="0 0 40 40"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              className="transition-smooth"
            >
              <rect width="40" height="40" rx="8" fill="url(#gradient)" />
              <path
                d="M20 10L12 16V28L20 34L28 28V16L20 10Z"
                stroke="white"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M20 10V22M20 22L12 28M20 22L28 28"
                stroke="white"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <defs>
                <linearGradient
                  id="gradient"
                  x1="0"
                  y1="0"
                  x2="40"
                  y2="40"
                  gradientUnits="userSpaceOnUse"
                >
                  <stop stopColor="#2563EB" />
                  <stop offset="1" stopColor="#7C3AED" />
                </linearGradient>
              </defs>
            </svg>
            <span className="font-heading text-xl font-semibold text-foreground">
              InterviewNinja
            </span>
          </div>
        </Link>

        <div className="hidden lg:flex items-center gap-6">
          {navigationItems.map((item) => (
            <Link
              key={item.path}
              href={item.path}
              className={`
                flex items-center gap-6 px-18 py-12 rounded-md
                transition-smooth font-medium text-sm
                ${
                  isActivePath(item.path)
                    ? 'bg-primary text-primary-foreground shadow-glow'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                }
              `}
            >
              <Icon name={item.icon as any} size={20} variant="outline" />
              <span>{item.label}</span>
            </Link>
          ))}
        </div>

        <button
          onClick={toggleMobileMenu}
          className="lg:hidden p-12 rounded-md hover:bg-muted transition-smooth focus-ring"
          aria-label="Toggle mobile menu"
          aria-expanded={mobileMenuOpen}
        >
          <Icon
            name={mobileMenuOpen ? 'XMarkIcon' : 'Bars3Icon'}
            size={24}
            variant="outline"
          />
        </button>
      </nav>

      {mobileMenuOpen && (
        <div className="lg:hidden bg-card border-t border-border">
          <div className="px-24 py-18 flex flex-col gap-6">
            {navigationItems.map((item) => (
              <Link
                key={item.path}
                href={item.path}
                onClick={closeMobileMenu}
                className={`
                  flex items-center gap-12 px-18 py-12 rounded-md
                  transition-smooth font-medium text-sm
                  ${
                    isActivePath(item.path)
                      ? 'bg-primary text-primary-foreground shadow-glow'
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                  }
                `}
              >
                <Icon name={item.icon as any} size={20} variant="outline" />
                <span>{item.label}</span>
              </Link>
            ))}
          </div>
        </div>
      )}
    </header>
  );
}
import React from 'react';
import { Head, Link, usePage } from '@inertiajs/react';
import type { PageProps } from '@/types';
import { home, dashboard } from '@/routes';
import { form } from '@/routes/contact';

interface AppLayoutProps {
    title?: string;
    children: React.ReactNode;
}

export default function AppLayout({ title = 'Customer Dashboard', children }: AppLayoutProps) {
    const { url } = usePage<PageProps>();
    
    const isActive = (path: string) => {
        return url === path ? 'bg-gray-900 text-white' : 'text-gray-300 hover:bg-gray-700 hover:text-white';
    };
    
    return (
        <>
            <Head title={title} />
            <div className="min-h-screen bg-gray-50">
                <nav className="bg-gray-800">
                    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                        <div className="flex h-16 items-center justify-between">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <span className="text-white text-xl font-bold">Customer Dashboard</span>
                                </div>
                                <div className="ml-10 flex items-baseline space-x-4">
                                    <Link
                                        href={home()}
                                        className={`${isActive('/')} rounded-md px-3 py-2 text-sm font-medium`}
                                        preserveState
                                    >
                                        Home
                                    </Link>
                                    <Link
                                        href={dashboard()}
                                        className={`${isActive('/dashboard')} rounded-md px-3 py-2 text-sm font-medium`}
                                        preserveState
                                    >
                                        Dashboard
                                    </Link>
                                    <Link
                                        href={form()}
                                        className={`${isActive('/contact')} rounded-md px-3 py-2 text-sm font-medium`}
                                        preserveState
                                    >
                                        Contact Form
                                    </Link>
                                </div>
                            </div>
                        </div>
                    </div>
                </nav>
                <header className="bg-white shadow">
                    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
                        <h1 className="text-3xl font-bold tracking-tight text-gray-900">
                            {title}
                        </h1>
                    </div>
                </header>
                <main>
                    <div className="mx-auto max-w-7xl py-6 sm:px-6 lg:px-8">
                        {children}
                    </div>
                </main>
            </div>
        </>
    );
}
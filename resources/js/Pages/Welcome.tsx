import type {PageProps} from '@/types';
import { Link } from '@inertiajs/react';
import AppLayout from '@/Layouts/AppLayout';
import * as Dialog from '@radix-ui/react-dialog';
import { Cross1Icon } from '@radix-ui/react-icons';

export default function Welcome({ }: PageProps) {
    return (
        <AppLayout title="Welcome">
            <div className="overflow-hidden bg-white py-24 sm:py-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto grid max-w-2xl grid-cols-1 gap-x-8 gap-y-16 sm:gap-y-20 lg:mx-0 lg:max-w-none lg:grid-cols-2">
                        <div className="lg:pr-8 lg:pt-4">
                            <div className="lg:max-w-lg">
                                <h2 className="text-base font-semibold leading-7 text-indigo-600">
                                    Welcome to
                                </h2>
                                <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
                                    Customer Dashboard
                                </p>
                                <p className="mt-6 text-lg leading-8 text-gray-600">
                                    Built with Laravel 12, React 19, Inertia.js, and Radix UI. This is a modern,
                                    full-stack application with seamless SPA experience.
                                </p>
                                
                                <div className="mt-8 flex gap-4">
                                    <Link
                                        href="/dashboard"
                                        className="inline-flex items-center gap-x-2 rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                                    >
                                        View Dashboard
                                    </Link>
                                    
                                    <Dialog.Root>
                                        <Dialog.Trigger asChild>
                                            <button className="inline-flex items-center gap-x-2 rounded-md bg-gray-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-gray-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gray-600">
                                                Try Radix UI Dialog
                                            </button>
                                        </Dialog.Trigger>
                                        <Dialog.Portal>
                                            <Dialog.Overlay className="fixed inset-0 bg-black/50" />
                                            <Dialog.Content className="fixed top-1/2 left-1/2 max-h-[85vh] w-[90vw] max-w-[450px] translate-x-[-50%] translate-y-[-50%] rounded-md bg-white p-6 shadow-lg">
                                                <Dialog.Title className="text-lg font-semibold text-gray-900 mb-4">
                                                    Radix UI Dialog Example
                                                </Dialog.Title>
                                                <Dialog.Description className="text-sm text-gray-600 mb-6">
                                                    This is an example dialog built with Radix UI. It's fully accessible
                                                    and customizable with your own styling.
                                                </Dialog.Description>
                                                <div className="flex justify-end gap-4">
                                                    <Dialog.Close asChild>
                                                        <button className="inline-flex items-center gap-x-2 rounded-md bg-gray-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-gray-500">
                                                            Close
                                                        </button>
                                                    </Dialog.Close>
                                                </div>
                                                <Dialog.Close asChild>
                                                    <button
                                                        className="absolute top-4 right-4 inline-flex h-6 w-6 appearance-none items-center justify-center rounded-full text-gray-500 hover:text-gray-700"
                                                        aria-label="Close"
                                                    >
                                                        <Cross1Icon />
                                                    </button>
                                                </Dialog.Close>
                                            </Dialog.Content>
                                        </Dialog.Portal>
                                    </Dialog.Root>
                                </div>

                                <div className="mt-10">
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                                        Technology Stack
                                    </h3>
                                    <ul className="space-y-2 text-sm text-gray-600">
                                        <li>• Laravel 12 - Backend framework</li>
                                        <li>• React 19 - Frontend library with latest features</li>
                                        <li>• Inertia.js 2 - SPA without API complexity</li>
                                        <li>• Radix UI - Accessible component library</li>
                                        <li>• TypeScript - Type safety</li>
                                        <li>• Tailwind CSS 4 - Utility-first styling</li>
                                        <li>• Docker - Containerized development</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
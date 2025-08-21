import type {PageProps} from '@/types';
import { Link } from '@inertiajs/react';
import AppLayout from '@/Layouts/AppLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/Components/Card';
import { Button } from '@/Components/Button';
import { DropdownMenu } from 'radix-ui';
import {DotsVerticalIcon, PersonIcon, MixIcon, GearIcon } from '@radix-ui/react-icons';

export default function Dashboard({ }: PageProps) {
    return (
        <AppLayout title="Dashboard">
            <div className="space-y-6">
                {/* Welcome Section */}
                <div className="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div className="p-6 text-gray-900">
                        <h2 className="text-2xl font-bold mb-4">Welcome to your dashboard!</h2>
                        <p className="text-gray-600">
                            This is a sample dashboard built with Laravel 12, React 19, Inertia.js, and Radix UI components.
                        </p>
                    </div>
                </div>

                {/* Stats Cards */}
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">
                                Total Users
                            </CardTitle>
                            <PersonIcon className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">1,234</div>
                            <p className="text-xs text-muted-foreground">
                                +12% from last month
                            </p>
                        </CardContent>
                    </Card>
                    
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">
                                Active Sessions
                            </CardTitle>
                            <MixIcon className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">573</div>
                            <p className="text-xs text-muted-foreground">
                                +5% from last hour
                            </p>
                        </CardContent>
                    </Card>
                    
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">
                                System Status
                            </CardTitle>
                            <GearIcon className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-green-600">Healthy</div>
                            <p className="text-xs text-muted-foreground">
                                All systems operational
                            </p>
                        </CardContent>
                    </Card>
                </div>

                {/* Actions Section */}
                <Card>
                    <CardHeader>
                        <CardTitle>Quick Actions</CardTitle>
                        <CardDescription>
                            Common tasks and operations you can perform
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex flex-wrap gap-4">
                            <Link href="/contact" preserveScroll>
                                <Button>Contact Form Example</Button>
                            </Link>
                            <Link 
                                href="/dashboard" 
                                preserveState
                                only={['stats']}
                            >
                                <Button variant="secondary">Refresh Stats</Button>
                            </Link>
                            <Link href="/" as="button" method="get">
                                <Button variant="ghost">Home Page</Button>
                            </Link>
                            
                            <DropdownMenu.Root>
                                <DropdownMenu.Trigger asChild>
                                    <Button variant="ghost" size="sm">
                                        <DotsVerticalIcon className="h-4 w-4" />
                                    </Button>
                                </DropdownMenu.Trigger>
                                <DropdownMenu.Portal>
                                    <DropdownMenu.Content
                                        className="min-w-[180px] bg-white rounded-md p-1 shadow-lg border border-gray-200"
                                        sideOffset={5}
                                    >
                                        <DropdownMenu.Item className="text-sm rounded px-2 py-1.5 cursor-pointer hover:bg-gray-50 focus:bg-gray-50 outline-none">
                                            Settings
                                        </DropdownMenu.Item>
                                        <DropdownMenu.Item className="text-sm rounded px-2 py-1.5 cursor-pointer hover:bg-gray-50 focus:bg-gray-50 outline-none">
                                            Support
                                        </DropdownMenu.Item>
                                        <DropdownMenu.Separator className="h-px bg-gray-200 my-1" />
                                        <DropdownMenu.Item className="text-sm rounded px-2 py-1.5 cursor-pointer hover:bg-gray-50 focus:bg-gray-50 outline-none">
                                            Documentation
                                        </DropdownMenu.Item>
                                    </DropdownMenu.Content>
                                </DropdownMenu.Portal>
                            </DropdownMenu.Root>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </AppLayout>
    );
}
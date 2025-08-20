import { Head } from '@inertiajs/react';
import { Button } from '@/Components/Button';

interface ErrorPageProps {
    status: number;
    message?: string;
}

const errorMessages: Record<number, { title: string; description: string }> = {
    403: {
        title: 'Forbidden',
        description: 'Sorry, you are not authorized to access this page.',
    },
    404: {
        title: 'Page Not Found',
        description: 'Sorry, the page you are looking for could not be found.',
    },
    419: {
        title: 'Session Expired',
        description: 'Sorry, your session has expired. Please refresh and try again.',
    },
    429: {
        title: 'Too Many Requests',
        description: 'Sorry, you are making too many requests. Please slow down.',
    },
    500: {
        title: 'Server Error',
        description: 'Oops, something went wrong on our servers.',
    },
    503: {
        title: 'Service Unavailable',
        description: 'Sorry, we are doing some maintenance. Please check back soon.',
    },
};

export default function Error({ status, message }: ErrorPageProps) {
    const error = errorMessages[status] || {
        title: `Error ${status}`,
        description: message || 'An unexpected error occurred.',
    };

    const handleGoHome = () => {
        window.location.href = '/';
    };

    const handleGoBack = () => {
        window.history.back();
    };

    const handleRefresh = () => {
        window.location.reload();
    };

    return (
        <>
            <Head title={`${status} - ${error.title}`} />
            
            <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4 sm:px-6 lg:px-8">
                <div className="max-w-md w-full space-y-8 text-center">
                    <div>
                        <h1 className="text-9xl font-extrabold text-gray-900 tracking-wider">
                            {status}
                        </h1>
                        <h2 className="mt-6 text-3xl font-bold text-gray-900">
                            {error.title}
                        </h2>
                        <p className="mt-2 text-lg text-gray-600">
                            {error.description}
                        </p>
                    </div>

                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        {status === 419 ? (
                            <Button onClick={handleRefresh} className="w-full sm:w-auto">
                                Refresh Page
                            </Button>
                        ) : (
                            <>
                                <Button onClick={handleGoHome} className="w-full sm:w-auto">
                                    Go Home
                                </Button>
                                <Button 
                                    onClick={handleGoBack} 
                                    variant="secondary"
                                    className="w-full sm:w-auto"
                                >
                                    Go Back
                                </Button>
                            </>
                        )}
                    </div>

                    {status === 500 && (
                        <div className="mt-8 p-4 bg-red-50 rounded-lg">
                            <p className="text-sm text-red-800">
                                Our team has been notified and we're working to fix this issue.
                                Please try again later.
                            </p>
                        </div>
                    )}

                    {status === 503 && (
                        <div className="mt-8 p-4 bg-yellow-50 rounded-lg">
                            <p className="text-sm text-yellow-800">
                                We're performing scheduled maintenance. 
                                Please check back in a few minutes.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}
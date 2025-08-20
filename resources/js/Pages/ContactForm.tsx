import type { FormEvent } from 'react';
import { useForm } from '@inertiajs/react';
import type { PageProps } from '@/types';
import AppLayout from '@/Layouts/AppLayout';
import { Button } from '@/Components/Button';

export default function ContactForm({ }: PageProps) {
    const { data, setData, post, processing, errors, reset, clearErrors } = useForm({
        name: '',
        email: '',
        subject: '',
        message: '',
    });

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        
        post('/contact', {
            preserveState: true,
            preserveScroll: true,
            onSuccess: () => {
                reset();
                alert('Form submitted successfully!');
            },
            onError: () => {
                console.log('Form submission errors:', errors);
            },
        });
    };

    return (
        <AppLayout title="Contact Form">
            <div className="max-w-2xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
                <div className="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                    <div className="p-6">
                        <h2 className="text-2xl font-bold mb-6">Contact Us</h2>
                        <p className="text-gray-600 mb-8">
                            This is an example form demonstrating Inertia's useForm hook with validation.
                        </p>

                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div>
                                <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                                    Name
                                </label>
                                <input
                                    type="text"
                                    id="name"
                                    value={data.name}
                                    onChange={(e) => {
                                        setData('name', e.target.value);
                                        clearErrors('name');
                                    }}
                                    className={`mt-1 block w-full rounded-md shadow-sm ${
                                        errors.name 
                                            ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
                                            : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'
                                    } sm:text-sm`}
                                    disabled={processing}
                                />
                                {errors.name && (
                                    <p className="mt-1 text-sm text-red-600">{errors.name}</p>
                                )}
                            </div>

                            <div>
                                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                                    Email
                                </label>
                                <input
                                    type="email"
                                    id="email"
                                    value={data.email}
                                    onChange={(e) => {
                                        setData('email', e.target.value);
                                        clearErrors('email');
                                    }}
                                    className={`mt-1 block w-full rounded-md shadow-sm ${
                                        errors.email 
                                            ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
                                            : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'
                                    } sm:text-sm`}
                                    disabled={processing}
                                />
                                {errors.email && (
                                    <p className="mt-1 text-sm text-red-600">{errors.email}</p>
                                )}
                            </div>

                            <div>
                                <label htmlFor="subject" className="block text-sm font-medium text-gray-700">
                                    Subject
                                </label>
                                <input
                                    type="text"
                                    id="subject"
                                    value={data.subject}
                                    onChange={(e) => {
                                        setData('subject', e.target.value);
                                        clearErrors('subject');
                                    }}
                                    className={`mt-1 block w-full rounded-md shadow-sm ${
                                        errors.subject 
                                            ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
                                            : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'
                                    } sm:text-sm`}
                                    disabled={processing}
                                />
                                {errors.subject && (
                                    <p className="mt-1 text-sm text-red-600">{errors.subject}</p>
                                )}
                            </div>

                            <div>
                                <label htmlFor="message" className="block text-sm font-medium text-gray-700">
                                    Message
                                </label>
                                <textarea
                                    id="message"
                                    rows={4}
                                    value={data.message}
                                    onChange={(e) => {
                                        setData('message', e.target.value);
                                        clearErrors('message');
                                    }}
                                    className={`mt-1 block w-full rounded-md shadow-sm ${
                                        errors.message 
                                            ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
                                            : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'
                                    } sm:text-sm`}
                                    disabled={processing}
                                />
                                {errors.message && (
                                    <p className="mt-1 text-sm text-red-600">{errors.message}</p>
                                )}
                            </div>

                            <div className="flex items-center justify-between">
                                <Button
                                    type="submit"
                                    disabled={processing}
                                    className={processing ? 'opacity-50 cursor-not-allowed' : ''}
                                >
                                    {processing ? 'Submitting...' : 'Submit'}
                                </Button>

                                <Button
                                    type="button"
                                    variant="ghost"
                                    onClick={() => reset()}
                                    disabled={processing}
                                >
                                    Reset Form
                                </Button>
                            </div>
                        </form>

                        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
                            <h3 className="text-sm font-semibold text-blue-900 mb-2">Form State Demo</h3>
                            <p className="text-xs text-blue-700">
                                This form demonstrates:
                            </p>
                            <ul className="mt-2 text-xs text-blue-700 list-disc list-inside space-y-1">
                                <li>useForm hook for form state management</li>
                                <li>Real-time validation error display</li>
                                <li>Loading states during submission</li>
                                <li>Form reset functionality</li>
                                <li>Error clearing on input change</li>
                                <li>Preserve scroll position on submission</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
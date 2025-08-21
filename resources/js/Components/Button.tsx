import * as React from 'react';
import { Slot } from 'radix-ui';
import { cn } from '@/lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    asChild?: boolean;
    variant?: 'default' | 'secondary' | 'ghost' | 'destructive';
    size?: 'default' | 'sm' | 'lg';
    ref?: React.Ref<HTMLButtonElement>;
}

const Button = ({ className, variant = 'default', size = 'default', asChild = false, ref, ...props }: ButtonProps) => {
        if (asChild) {
            return (
                <Slot.Slot
                    className={cn(
                        'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors',
                        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
                        'disabled:pointer-events-none disabled:opacity-50',
                        {
                            'bg-primary text-primary-foreground hover:bg-primary/90': variant === 'default',
                            'bg-secondary text-secondary-foreground hover:bg-secondary/80': variant === 'secondary', 
                            'hover:bg-accent hover:text-accent-foreground': variant === 'ghost',
                            'bg-destructive text-destructive-foreground hover:bg-destructive/90': variant === 'destructive',
                        },
                        {
                            'h-10 px-4 py-2': size === 'default',
                            'h-9 px-3 text-xs': size === 'sm',
                            'h-11 px-8': size === 'lg',
                        },
                        className
                    )}
                    {...props}
                />
            );
        }
        
        return (
            <button
                className={cn(
                    'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors',
                    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
                    'disabled:pointer-events-none disabled:opacity-50',
                    {
                        'bg-primary text-primary-foreground hover:bg-primary/90': variant === 'default',
                        'bg-secondary text-secondary-foreground hover:bg-secondary/80': variant === 'secondary', 
                        'hover:bg-accent hover:text-accent-foreground': variant === 'ghost',
                        'bg-destructive text-destructive-foreground hover:bg-destructive/90': variant === 'destructive',
                    },
                    {
                        'h-10 px-4 py-2': size === 'default',
                        'h-9 px-3 text-xs': size === 'sm',
                        'h-11 px-8': size === 'lg',
                    },
                    className
                )}
                ref={ref}
                {...props}
            />
        );
};

export { Button };
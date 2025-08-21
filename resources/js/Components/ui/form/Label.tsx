import * as React from 'react';
import { Label as RadixLabel } from 'radix-ui';
import { cn } from '@/lib/utils';

interface LabelProps extends React.ComponentPropsWithoutRef<typeof RadixLabel.Root> {
    ref?: React.Ref<React.ComponentRef<typeof RadixLabel.Root>>;
}

const Label = ({ className, ref, ...props }: LabelProps) => (
    <RadixLabel.Root
        ref={ref}
        className={cn(
            'text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
            className
        )}
        {...props}
    />
);

export { Label };
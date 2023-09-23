import cn from '@/lib/cn';
import { ButtonHTMLAttributes } from 'react';

interface MainButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  isActive?: boolean;
}

function MainButton(props: MainButtonProps) {
  return (
    <button
      {...props}
      className={cn(
        'px-6 py-2 font-medium tracking-wide text-brand capitalize transition-colors duration-300 transform bg-brand-600 rounded-lg hover:bg-brand-500 focus:outline-none focus:ring focus:ring-brand-300 focus:ring-opacity-80 bg-inherit border border-brand-500 hover:text-white',
        props.className,
        {
          'bg-brand text-white hover:bg-brand/80': props.isActive,
        },
      )}
    >
      {props.children}
    </button>
  );
}
export default MainButton;

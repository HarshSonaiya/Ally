import React, { useState, useEffect, useRef, useContext } from 'react';
import ReactDOM from 'react-dom';
import './Popover.css';  // Import your regular CSS file
import PropTypes from 'prop-types';
import { cva } from 'class-variance-authority';

// Create a context to share the trigger ref
const TriggerContext = React.createContext(null);

const popoverVariants = cva('popover', {
    variants: {
        align: {
            top: 'top',
            'top-right': 'top-right',
            right: 'right',
            'bottom-right': 'bottom-right',
            bottom: 'bottom',
            'bottom-left': 'bottom-left',
            left: 'left',
            'top-left': 'top-left',
            center: 'center',
        },
    },
    defaultVariants: {
        align: 'center',
    },
});

// PopoverRoot component
export function PopoverRoot({ children, className }) {
    const triggerRef = useRef(null);
    return (
        <TriggerContext.Provider value={triggerRef}>
            <div className={className}>{children}</div>
        </TriggerContext.Provider>
    );
}

// Popover component
export function Popover({
    children,
    visible,
    onClose,
    className,
    style,
    align = 'center',
    offset = 16,
}) {
    const [position, setPosition] = useState({ top: 0, left: 0 });
    const popoverRef = useRef(null);
    const triggerRef = useContext(TriggerContext);

    const calculatePosition = () => {
        if (!popoverRef.current || !visible) return;

        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;
        const popoverRect = popoverRef.current.getBoundingClientRect();
        const popoverWidth = popoverRect.width;
        const popoverHeight = popoverRect.height;

        let top = 0;
        let left = 0;

        switch (align) {
            case 'top':
                top = offset;
                left = (windowWidth - popoverWidth) / 2;
                break;
            case 'top-right':
                top = offset;
                left = windowWidth - popoverWidth - offset;
                break;
            case 'right':
                top = (windowHeight - popoverHeight) / 2;
                left = windowWidth - popoverWidth - offset;
                break;
            case 'bottom-right':
                top = windowHeight - popoverHeight - offset;
                left = windowWidth - popoverWidth - offset;
                break;
            case 'bottom':
                top = windowHeight - popoverHeight - offset;
                left = (windowWidth - popoverWidth) / 2;
                break;
            case 'bottom-left':
                top = windowHeight - popoverHeight - offset;
                left = offset;
                break;
            case 'left':
                top = (windowHeight - popoverHeight) / 2;
                left = offset;
                break;
            case 'top-left':
                top = offset;
                left = offset;
                break;
            case 'center':
                top = (windowHeight - popoverHeight) / 2;
                left = (windowWidth - popoverWidth) / 2;
                break;
        }

        top = Math.max(
            offset,
            Math.min(top, windowHeight - popoverHeight - offset)
        );
        left = Math.max(
            offset,
            Math.min(left, windowWidth - popoverWidth - offset)
        );

        return { top, left };
    };

    useEffect(() => {
        if (visible) {
            const newPosition = calculatePosition();
            if (newPosition) {
                setPosition(newPosition);
            }
        }
    }, [visible, align, offset]);

    useEffect(() => {
        const handleResize = () => {
            const newPosition = calculatePosition();
            if (newPosition) {
                setPosition(newPosition);
            }
        };

        if (visible) {
            window.addEventListener('resize', handleResize);
            window.addEventListener('scroll', handleResize);
        }

        return () => {
            window.removeEventListener('resize', handleResize);
            window.removeEventListener('scroll', handleResize);
        };
    }, [visible, align, offset]);

    useEffect(() => {
        const handleClickOutside = (e) => {
            if (
                popoverRef.current &&
                !popoverRef.current.contains(e.target) &&
                !triggerRef?.current?.contains(e.target)
            ) {
                onClose();
            }
        };

        if (visible) {
            document.addEventListener('click', handleClickOutside);
        }
        return () => {
            document.removeEventListener('click', handleClickOutside);
        };
    }, [onClose, visible]);

    if (!visible) return null;

    return ReactDOM.createPortal(
        <div
            className={`popover ${popoverVariants({ align })} ${visible ? 'visible' : ''} ${className}`}
            ref={popoverRef}
            style={{
                ...(!style?.top && !style?.left
                    ? {
                        top: `${position.top}px`,
                        left: `${position.left}px`,
                    }
                    : {}),
                ...style,
            }}
        >
            {children}
        </div>,
        document.body
    );
}
Popover.propTypes = {
    children: PropTypes.node.isRequired,
    visible: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    className: PropTypes.string,
    style: PropTypes.object,
    align: PropTypes.oneOf([
        'top', 'top-right', 'right', 'bottom-right', 'bottom', 'bottom-left', 'left', 'top-left', 'center'
    ]),
    offset: PropTypes.number,
};

// PopoverTrigger component
// PopoverTrigger component
export function PopoverTrigger({ children, onClick, className }) {
    const triggerRef = useContext(TriggerContext);

    return (
        <div
            ref={triggerRef}
            className={`popoverTrigger ${className}`}
            onClick={onClick}
            aria-haspopup="true"
            aria-expanded="true"
        >
            {children}
        </div>
    );
}

// PopoverContent component
export function PopoverContent({ children, className }) {
    return <div className={`popoverContent ${className}`}>{children}</div>;
}

// PopoverHeader component
export function PopoverHeader({ children, className }) {
    return <div className={`popoverHeader ${className}`}>{children}</div>;
}

// PopoverFooter component
export function PopoverFooter({ children, className }) {
    return <div className={`popoverFooter ${className}`}>{children}</div>;
}

// PopoverTitle component
export function PopoverTitle({ children, className }) {
    return <h3 className={`popoverTitle ${className}`}>{children}</h3>;
}

// PopoverAction component
export function PopoverAction({ children, className, onClick }) {
    return (
        <div
            className={`popoverTrigger ${className}`}
            onClick={onClick}
            aria-haspopup="true"
            aria-expanded="true"
        >
            {children}
        </div>
    );
}

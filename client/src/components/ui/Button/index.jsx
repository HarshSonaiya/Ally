import React from "react";
import PropTypes from "prop-types";
import { cva } from "class-variance-authority";
import styles from "./Button.module.css";

// Use cva to define the dynamic class names
const buttonVariants = cva(
  [styles.button], // Base styles from CSS Module
  {
    variants: {
      variant: {
        default: styles.variantDefault,
        destructive: styles.variantDestructive,
        outline: styles.variantOutline,
        secondary: styles.variantSecondary,
        ghost: styles.variantGhost,
        link: styles.variantLink,
      },
      size: {
        default: styles.sizeDefault,
        sm: styles.sizeSm,
        lg: styles.sizeLg,
        icon: styles.sizeIcon,
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

// Define prop types explicitly
// interface ButtonProps {
//   variant?:
//   | "default"
//   | "destructive"
//   | "outline"
//   | "secondary"
//   | "ghost"
//   | "link";
//   size?: "default" | "sm" | "lg" | "icon";
//   //   children: React.ReactNode;
//   disabled?: boolean;
// }

const Button = ({
  variant = "default",
  size = "default",
  disabled = false,
  ...props
}) => {
  // Apply the cva function to dynamically generate the class names
  const buttonClass = buttonVariants({ variant, size });

  return <button className={buttonClass} disabled={disabled} {...props} />;
};
Button.propTypes = {
  variant: PropTypes.oneOf([
    "default",
    "destructive",
    "outline",
    "secondary",
    "ghost",
    "link",
  ]),
  size: PropTypes.oneOf(["default", "sm", "lg", "icon"]),
  disabled: PropTypes.bool,
};

export default Button;

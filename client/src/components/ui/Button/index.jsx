import React from "react";
import PropTypes from "prop-types";
import { cva } from "class-variance-authority";
import clsx from "clsx";
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
        default: styles.sizeMd,
        sm: styles.sizeSm,
        md: styles.sizeMd,
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

const Button = ({
  variant = "default",
  size = "default",
  disabled = false,
  className = "",
  ...props
}) => {
  // Apply the cva function to dynamically generate the class names
  const buttonClass = buttonVariants({ variant, size });

  const combinedClass = clsx(buttonClass, className);

  return <button className={combinedClass} disabled={disabled} {...props} />;
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
  className: PropTypes.string,
};

export default Button;

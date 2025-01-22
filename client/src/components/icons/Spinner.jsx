// import React from "react";
// import PropTypes from "prop-types";

// import { cssValue } from "./helpers/unitConverter";
// import { createAnimation } from "./helpers/animation";

// const bounce = createAnimation(
//     "BounceLoader",
//     "0% {transform: scale(0)} 50% {transform: scale(1.0)} 100% {transform: scale(0)}",
//     "bounce"
// );

// function BounceLoader({
//     loading = true,
//     color = "#000000",
//     speedMultiplier = 1,
//     cssOverride = {},
//     size = 60,
//     ...additionalprops
// }) {
//     const style = (i) => {
//         const animationTiming = i === 1 ? `${1 / speedMultiplier}s` : "0s";
//         return {
//             position: "absolute",
//             height: cssValue(size),
//             width: cssValue(size),
//             backgroundColor: color,
//             borderRadius: "100%",
//             opacity: 0.6,
//             top: 0,
//             left: 0,
//             animationFillMode: "both",
//             animation: `${bounce} ${2.1 / speedMultiplier}s ${animationTiming} infinite ease-in-out`,
//         };
//     };

//     const wrapper = {
//         display: "inherit",
//         position: "relative",
//         width: cssValue(size),
//         height: cssValue(size),
//         ...cssOverride,
//     };

//     if (!loading) {
//         return null;
//     }

//     return (
//         <span style={wrapper} {...additionalprops}>
//             <span style={style(1)} />
//             <span style={style(2)} />
//         </span>
//     );
// }
// BounceLoader.propTypes = {
//     loading: PropTypes.bool,
//     color: PropTypes.string,
//     speedMultiplier: PropTypes.number,
//     cssOverride: PropTypes.object,
//     size: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
// };

// export default BounceLoader;

import PropTypes from "prop-types";
import { cssValue } from "./helpers/unitConverter";
import { createAnimation } from "./helpers/animation";

const skew = createAnimation(
    "SkewLoader",
    "25% {transform: perspective(100px) rotateX(180deg) rotateY(0)} 50% {transform: perspective(100px) rotateX(180deg) rotateY(180deg)} 75% {transform: perspective(100px) rotateX(0) rotateY(180deg)} 100% {transform: perspective(100px) rotateX(0) rotateY(0)}",
    "skew"
);

function SkewLoader({
    loading = true,
    color = "#000000",
    speedMultiplier = 1,
    cssOverride = {},
    size = 20,
    ...additionalprops
}) {
    const style = {
        width: "0",
        height: "0",
        borderLeft: `${cssValue(size)} solid transparent`,
        borderRight: `${cssValue(size)} solid transparent`,
        borderBottom: `${cssValue(size)} solid ${color}`,
        display: "inline-block",
        animation: `${skew} ${3 / speedMultiplier}s 0s infinite cubic-bezier(0.09, 0.57, 0.49, 0.9)`,
        animationFillMode: "both",
        ...cssOverride,
    };

    if (!loading) {
        return null;
    }

    return <span style={style} {...additionalprops} />;
}

SkewLoader.propTypes = {
    loading: PropTypes.bool,
    color: PropTypes.string,
    speedMultiplier: PropTypes.number,
    cssOverride: PropTypes.object,
    size: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
};

export default SkewLoader;

import "./icons.css";

export default function PlusIcon(props) {
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            className="plus-icon"
            {...props}
        >
            <path d="M5 12h14" />
            <path d="M12 5v14" />
        </svg>
    );
}

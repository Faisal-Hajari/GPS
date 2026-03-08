interface Option<T extends string> {
    value: T;
    label: string;
}

interface LayerToggleButtonProps<T extends string> {
    options: [Option<T>, Option<T>];
    active: T;
    onChange: (value: T) => void;
}

export default function LayerToggleButton<T extends string>({ options, active, onChange }: LayerToggleButtonProps<T>) {
    return (
        <div style={{ display: "flex", borderRadius: 6, overflow: "hidden", border: "1px solid #ccc" }}>
            {options.map(o => (
                <button
                    key={o.value}
                    onClick={() => onChange(o.value)}
                    disabled={o.value === active}
                    style={{
                        flex: 1,
                        padding: "6px 14px",
                        cursor: o.value === active ? "default" : "pointer",
                        background: o.value === active ? "#0066cc" : "#fff",
                        color: o.value === active ? "#fff" : "#333",
                        border: "none",
                        fontWeight: o.value === active ? 600 : 400,
                        transition: "background 0.15s, color 0.15s",
                    }}
                >
                    {o.label}
                </button>
            ))}
        </div>
    );
}

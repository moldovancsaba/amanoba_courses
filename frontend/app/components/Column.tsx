interface ColumnProps {
    title: string;
    tasks: string[];
}

export default function Column({ title, tasks }: ColumnProps) {
    return (
        <div className="w-64 bg-white p-4 rounded shadow">
            <h2 className="text-lg font-semibold mb-2">{title}</h2>
            <div className="space-y-2">
                {tasks.map((task, index) => (
                    <div key={index} className="bg-gray-200 p-2 rounded">
                        {task}
                    </div>
                ))}
            </div>
        </div>
    );
}
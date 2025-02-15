"use client";

import { useState } from "react";

interface AddNewTaskProps {
    onAddTask: (task: string) => void;
}

export default function AddNewTask({ onAddTask }: AddNewTaskProps) {
    const [newTask, setNewTask] = useState("NEW TASK");
    const [isEditing, setIsEditing] = useState(false);

    const handleDoubleClick = () => {
        setIsEditing(true);
    };

    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setNewTask(event.target.value);
    };

    const handleConfirm = () => {
        const trimmedTask = newTask.trim();

        if (trimmedTask === "" || trimmedTask === "NEW TASK") {
            setNewTask("NEW TASK"); // Reset without adding an empty task
            setIsEditing(false);
            return;
        }

        onAddTask(trimmedTask); // Send valid task to parent component
        setNewTask("NEW TASK"); // Reset input field
        setIsEditing(false);
    };

    const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === "Enter") {
            handleConfirm();
        } else if (event.key === "Escape") {
            setNewTask("NEW TASK"); // Reset if user cancels
            setIsEditing(false);
        }
    };

    return (
        <div
            className="bg-blue-100 p-3 rounded-md shadow cursor-pointer text-center border border-blue-300"
            onDoubleClick={handleDoubleClick}
        >
            {isEditing ? (
                <input
                    type="text"
                    className="w-full p-1 rounded border border-blue-300"
                    value={newTask}
                    onChange={handleChange}
                    onBlur={handleConfirm}
                    onKeyDown={handleKeyDown}
                    autoFocus
                />
            ) : (
                newTask
            )}
        </div>
    );
}
"use client";

import { useState, useEffect } from "react";
import { DragDropContext, Droppable, Draggable, DropResult } from "@hello-pangea/dnd";
import AddNewTask from "./AddNewTask";

const API_URL = "https://customato-prototype-backend.vercel.app/tasks";

interface Task {
    _id: string;
    title: string;
    status: "todo" | "wip" | "done" | "hold";
    position: number;
}

interface Tasks {
    [key: string]: Task[];
}

export default function KanbanBoard() {
    const [tasks, setTasks] = useState<Tasks>({ todo: [], wip: [], done: [], hold: [] });
    const [isEditing, setIsEditing] = useState<{ [key: string]: string | null }>({});
    const [isLoading, setIsLoading] = useState(true);
    const [hasError, setHasError] = useState(false);

    useEffect(() => {
        fetchTasks();
    }, []);

    const fetchTasks = async () => {
        try {
            const res = await fetch(API_URL);
            const data = await res.json();
            if (data && typeof data === "object") {
                // Sort tasks by position to maintain order
                Object.keys(data).forEach(key => {
                    data[key].sort((a: Task, b: Task) => a.position - b.position);
                });
                setTasks(data);
            } else {
                setTasks({ todo: [], wip: [], done: [], hold: [] });
            }
        } catch {
            setTasks({ todo: [], wip: [], done: [], hold: [] });
            setHasError(true);
        } finally {
            setIsLoading(false);
        }
    };

    const onDragEnd = async (result: DropResult) => {
        const { source, destination } = result;
        if (!destination) return;

        const sourceColumn = source.droppableId;
        const destColumn = destination.droppableId;

        if (!tasks[sourceColumn] || !tasks[destColumn]) return;

        const updatedTasks = { ...tasks };
        const movedTask = updatedTasks[sourceColumn].splice(source.index, 1)[0];

        if (movedTask) {
            movedTask.status = destColumn as Task["status"];
            updatedTasks[destColumn].splice(destination.index, 0, movedTask);

            // Update position in the column
            updatedTasks[destColumn].forEach((task, index) => {
                task.position = index;
            });

            setTasks(updatedTasks);
            await saveTaskPosition(movedTask._id, destColumn, destination.index);
        }
    };

    const handleDoubleClick = (columnId: string, taskId: string) => {
        setIsEditing({ ...isEditing, [taskId]: tasks[columnId].find(t => t._id === taskId)?.title || null });
    };

    const handleChange = async (taskId: string, columnId: string, newTitle: string) => {
        if (!newTitle.trim()) return;
        const updatedTasks = { ...tasks };
        const task = updatedTasks[columnId].find(t => t._id === taskId);
        if (task) {
            task.title = newTitle;
        }
        setTasks(updatedTasks);
        await updateTask(taskId, newTitle);
        setIsEditing({ ...isEditing, [taskId]: null });
    };

    const handleBlur = (taskId: string, columnId: string, newTitle: string) => {
        handleChange(taskId, columnId, newTitle);
    };

    const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>, taskId: string, columnId: string) => {
        if (event.key === "Enter") {
            handleChange(taskId, columnId, event.currentTarget.value);
        } else if (event.key === "Escape") {
            setIsEditing({ ...isEditing, [taskId]: null });
        }
    };

    const saveTaskPosition = async (taskId: string, newStatus: string, newPosition: number) => {
        await fetch(`${API_URL}/${taskId}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: newStatus, position: newPosition }),
        });
    };

    const updateTask = async (taskId: string, newTitle: string) => {
        await fetch(`${API_URL}/${taskId}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title: newTitle }),
        });
    };

    const handleAddTask = async (taskTitle: string) => {
        const newTask = { title: taskTitle, status: "todo", position: tasks.todo.length };
        await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(newTask),
        });
        fetchTasks();
    };

    return (
        <div className="flex items-center justify-center h-screen w-screen bg-gray-100 overflow-hidden">
            {isLoading ? (
                <p className="text-center text-lg text-gray-600">Loading...</p>
            ) : hasError ? (
                <p className="text-center text-lg text-red-500">Failed to load tasks.</p>
            ) : (
                <div className="flex w-full h-[80%] px-[3%] space-x-[2%]">
                    <DragDropContext onDragEnd={onDragEnd}>
                        {[
                            { id: "todo", title: "TODO", color: "bg-gray-500" },
                            { id: "wip", title: "WIP", color: "bg-blue-500" },
                            { id: "done", title: "DONE", color: "bg-green-500" },
                            { id: "hold", title: "HOLD", color: "bg-red-500" },
                        ].map(({ id, title, color }) => (
                            <Droppable key={id} droppableId={id}>
                                {(provided) => (
                                    <div
                                        ref={provided.innerRef}
                                        {...provided.droppableProps}
                                        className="w-[22%] bg-white p-4 rounded-lg shadow-md flex flex-col overflow-hidden"
                                    >
                                        <h2 className={`text-lg font-semibold mb-4 text-center p-2 rounded-md ${color} text-white`}>
                                            {title}
                                        </h2>
                                        {id === "todo" && (
                                            <div className="mb-3">
                                                <AddNewTask onAddTask={handleAddTask} />
                                            </div>
                                        )}
                                        <div className="space-y-3 flex-grow overflow-auto">
                                            {tasks[id]?.sort((a, b) => a.position - b.position).map((task, index) => (
                                                <Draggable key={task._id} draggableId={task._id} index={index}>
                                                    {(provided) => (
                                                        <div
                                                            ref={provided.innerRef}
                                                            {...provided.draggableProps}
                                                            {...provided.dragHandleProps}
                                                            className="bg-blue-100 p-3 rounded-md shadow cursor-pointer text-center border border-blue-300"
                                                            onDoubleClick={() => handleDoubleClick(id, task._id)}
                                                        >
                                                            {isEditing[task._id] !== undefined ? (
                                                                <input
                                                                    type="text"
                                                                    className="w-full p-1 rounded border border-blue-300"
                                                                    defaultValue={task.title}
                                                                    onBlur={(e) => handleBlur(task._id, id, e.target.value)}
                                                                    onKeyDown={(e) => handleKeyDown(e, task._id, id)}
                                                                    autoFocus
                                                                />
                                                            ) : (
                                                                task.title
                                                            )}
                                                        </div>
                                                    )}
                                                </Draggable>
                                            ))}
                                            {provided.placeholder}
                                        </div>
                                    </div>
                                )}
                            </Droppable>
                        ))}
                    </DragDropContext>
                </div>
            )}
        </div>
    );
}
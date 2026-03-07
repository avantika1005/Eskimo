const API_BASE = "/api";

async function fetchStudents() {
    try {
        const response = await fetch(`${API_BASE}/students`);
        if (!response.ok) throw new Error("Failed to fetch students");
        
        const students = await response.json();
        renderStudents(students);
    } catch (error) {
        console.error("Error fetching students:", error);
        document.getElementById('studentTableBody').innerHTML = `
            <tr>
                <td colspan="6" class="py-8 text-center text-red-600 font-bold">
                    Error loading data. Is the backend server running?
                </td>
            </tr>
        `;
    }
}

function renderStudents(students) {
    const tableBody = document.getElementById('studentTableBody');
    
    if (students.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="py-8 text-center text-gray-500 font-bold italic">
                    No students found. Please upload a CSV file first.
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = students.map(student => {
        let riskClass = "text-green-600";
        if (student.risk_level === "High") riskClass = "text-red-600";
        else if (student.risk_level === "Medium") riskClass = "text-yellow-600";

        return `
            <tr class="border-b border-purple-50 hover:bg-purple-50 transition-colors">
                <td class="py-4 px-4 font-bold text-gray-700">${student.student_id}</td>
                <td class="py-4 px-4 font-black text-purple-900 uppercase">${student.name}</td>
                <td class="py-4 px-4 font-bold text-gray-600">${student.grade_class}</td>
                <td class="py-4 px-4 font-black ${riskClass} uppercase">${student.risk_level || 'N/A'}</td>
                <td class="py-4 px-4 font-black text-gray-800">${student.risk_score || 0}%</td>
                <td class="py-4 px-4">
                    <a href="student-detail.html?id=${student.id}" 
                       class="bg-purple-900 text-white px-4 py-2 rounded-lg font-black text-xs hover:bg-purple-700 transition-all uppercase inline-block">
                        View Details
                    </a>
                </td>
            </tr>
        `;
    }).join('');
}

document.addEventListener("DOMContentLoaded", fetchStudents);

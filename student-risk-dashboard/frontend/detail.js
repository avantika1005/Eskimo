const API_BASE = "/api";

async function fetchStudentDetails() {
    const urlParams = new URLSearchParams(window.location.search);
    const studentId = urlParams.get('id');

    if (!studentId) {
        alert("Student ID missing in URL.");
        window.location.href = "students.html";
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/students/${studentId}`);
        if (!response.ok) throw new Error("Failed to fetch student details");
        
        const data = await response.json();
        renderDetail(data.student);
    } catch (error) {
        console.error("Error fetching details:", error);
        document.getElementById('loadingState').innerHTML = `
            <p class="text-red-600 text-xl font-black">ERROR LOADING STUDENT DATA. PLEASE TRY AGAIN LATER.</p>
        `;
    }
}

function renderDetail(student) {
    document.getElementById('loadingState').classList.add('hidden');
    document.getElementById('studentDetail').classList.remove('hidden');

    document.getElementById('disp_name').innerText = student.name;
    document.getElementById('disp_id').innerText = student.student_id;
    document.getElementById('disp_grade').innerText = student.grade_class;
    
    document.getElementById('disp_attendance').innerText = `${student.attendance_pct}%`;
    document.getElementById('disp_latest').innerText = student.latest_exam_score;
    document.getElementById('disp_previous').innerText = student.previous_exam_score;
    document.getElementById('disp_distance').innerText = `${student.distance_km} KM`;

    document.getElementById('disp_level').innerText = student.risk_level;
    document.getElementById('disp_score').innerText = `${student.risk_score}/100`;

    const riskBox = document.getElementById('risk_color_box');
    if (student.risk_level === 'High') {
        riskBox.className = 'md:col-span-1 p-8 rounded-2xl shadow-2xl border-l-[12px] border-red-900 bg-gradient-to-r from-red-600 to-red-500 flex flex-col justify-center text-white';
    } else if (student.risk_level === 'Medium') {
        riskBox.className = 'md:col-span-1 p-8 rounded-2xl shadow-2xl border-l-[12px] border-yellow-700 bg-gradient-to-r from-yellow-500 to-yellow-400 flex flex-col justify-center text-white';
    } else {
        riskBox.className = 'md:col-span-1 p-8 rounded-2xl shadow-2xl border-l-[12px] border-green-900 bg-gradient-to-r from-green-600 to-green-500 flex flex-col justify-center text-white';
    }

    const explanationText = document.getElementById('disp_explanation');
    const container = document.getElementById('llm_explanation_container');
    const noExplanation = document.getElementById('no_explanation');

    if (student.risk_level === 'Medium' || student.risk_level === 'High') {
        explanationText.innerText = student.llm_explanation || "No AI explanation available at this time.";
        container.classList.remove('hidden');
        noExplanation.classList.add('hidden');
    } else {
        container.classList.add('hidden');
        noExplanation.classList.remove('hidden');
    }
}

document.addEventListener("DOMContentLoaded", fetchStudentDetails);

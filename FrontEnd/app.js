/*
 * TeenShare Frontend Application
 * Handles all user interactions and connects to the backend API
 */

// Configuration - Change this to your deployed backend URL
const API_BASE_URL = 'https://teenshare.onrender.com';  // pointed to URL where backend is running

// Global variables to store scan results
let current_scan_results = null;
let current_text = '';
let has_file_attached = false;
let attached_file_name = '';

// Wait for page to load before running code
document.addEventListener('DOMContentLoaded', function() {
    console.log('TeenShare app loaded! 🛡️');
    initialize_app();
});

function initialize_app() {
    // Get all the elements we need from the page
    const text_input = document.getElementById('text-input');
    const file_upload = document.getElementById('file-upload');
    const scan_button = document.getElementById('scan-btn');
    const mask_button = document.getElementById('mask-btn');
    const preview_button = document.getElementById('preview-btn');
    const copy_button = document.getElementById('copy-btn');
    const start_over_button = document.getElementById('start-over-btn');
    
    // Set up event listeners (what happens when user clicks things)
    text_input.addEventListener('input', handle_text_input);
    file_upload.addEventListener('change', handle_file_upload);
    scan_button.addEventListener('click', start_scanning);
    mask_button.addEventListener('click', show_masked_content);
    preview_button.addEventListener('click', show_social_preview);
    copy_button.addEventListener('click', copy_masked_text);
    start_over_button.addEventListener('click', reset_app);
}

function handle_text_input(event) {
    // Update character count as user types
    const text = event.target.value;
    const char_count = text.length;
    const max_chars = 102400; // 100KB limit
    
    document.getElementById('char-count').textContent = 
        `${char_count.toLocaleString()} / ${max_chars.toLocaleString()} characters`;
    
    current_text = text;
}

function handle_file_upload(event) {
    // Handle when user attaches a file
    const file = event.target.files[0];
    
    if (file) {
        // Check file type
        const allowed_types = ['.pdf', '.doc', '.docx'];
        const file_extension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!allowed_types.includes(file_extension)) {
            alert('Please upload a PDF or Word document only!');
            event.target.value = ''; // Clear the file input
            return;
        }
        
        // Check file size (max 10MB)
        const max_size = 10 * 1024 * 1024; // 10MB in bytes
        if (file.size > max_size) {
            alert('File is too large! Please upload a file smaller than 10MB.');
            event.target.value = '';
            return;
        }
        
        // File is valid - update UI
        has_file_attached = true;
        attached_file_name = file.name;
        document.getElementById('file-name').textContent = `📎 ${file.name}`;
        console.log('File attached:', file.name);
    }
}

async function start_scanning() {
    // Get the text to scan
    const text_to_scan = document.getElementById('text-input').value;
    
    // Validate input
    if (!text_to_scan.trim() && !has_file_attached) {
        alert('Please enter some text or attach a document to scan!');
        return;
    }
    
    if (!text_to_scan.trim()) {
        alert('Please enter some text to scan! (Document scanning will be included in results)');
        return;
    }
    
    // Show scanning animation and hide other sections
    show_section('scanning');
    update_workflow_step(2); // Move to "Scan" step
    
    try {
        // Call the backend API
        console.log('Sending text to backend for scanning...');
        
        const response = await fetch(`${API_BASE_URL}/api/scan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text_content: text_to_scan,
                has_attachment: has_file_attached,
                attachment_name: attached_file_name
            })
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const results = await response.json();
        console.log('Scan results received:', results);
        
        // Store results for later use
        current_scan_results = results;
        
        // Wait a bit so user sees the scanning animation
        await sleep(1500);
        
        // Show the results
        display_scan_results(results);
        
    } catch (error) {
        console.error('Error scanning content:', error);
        alert('Oops! There was an error scanning your content. Make sure the backend server is running!');
        show_section('input');
        update_workflow_step(1);
    }
}

function display_scan_results(results) {
    // Show results section and update workflow
    show_section('results');
    update_workflow_step(3); // Move to "Review Results" step
    
    // Display risk meter
    display_risk_meter(results.risk_level, results.risk_score);
    
    // Display found entities
    display_findings(results.found_entities, results.educational_info);
    
    // Display attachment findings if present
    if (results.attachment_findings && results.attachment_findings.length > 0) {
        display_attachment_findings(results.attachment_findings);
    }
    
    // Display educational content
    display_educational_content(results.educational_info);
}

function display_risk_meter(risk_level, risk_score) {
    // Update the risk meter bar
    const meter_fill = document.getElementById('risk-meter-fill');
    const risk_badge = document.getElementById('risk-badge');
    const risk_score_element = document.getElementById('risk-score');
    
    // Animate the meter filling up
    setTimeout(() => {
        meter_fill.style.width = `${risk_score}%`;
    }, 100);
    
    // Update badge with proper styling
    risk_badge.textContent = risk_level;
    risk_badge.className = 'risk-badge ' + risk_level.toLowerCase();
    
    // Update score
    risk_score_element.textContent = `Score: ${risk_score}/100`;
}

function display_findings(found_entities, education_info) {
    const findings_list = document.getElementById('findings-list');
    const findings_summary = document.getElementById('findings-summary');
    
    // Update summary
    findings_summary.textContent = education_info.summary;
    
    // Clear previous findings
    findings_list.innerHTML = '';
    
    // Create a finding card for each entity
    found_entities.forEach((entity, index) => {
        const finding_card = document.createElement('div');
        finding_card.className = 'finding-item';
        finding_card.style.animationDelay = `${index * 0.1}s`;
        
        // Get nice display name for entity type
        const type_names = {
            'email': '📧 Email Address',
            'phone': '📱 Phone Number',
            'ssn': '🆔 Social Security Number',
            'credit_card': '💳 Credit Card',
            'drivers_license': '🚗 Driver\'s License',
            'name': '👤 Full Name',
            'address': '🏠 Address',
            'dob': '🎂 Date of Birth',
            'zip': '📮 ZIP Code'
        };
        
        const display_name = type_names[entity.type] || entity.type;
        const risk_level = entity.risk || 'medium';
        
        finding_card.innerHTML = `
            <div class="finding-header">
                <span class="finding-type">${display_name}</span>
                <span class="finding-risk ${risk_level}">${risk_level.toUpperCase()}</span>
            </div>
            <div class="finding-value">${entity.value}</div>
        `;
        
        findings_list.appendChild(finding_card);
    });
}

function display_attachment_findings(attachment_findings) {
    const attachment_section = document.getElementById('attachment-findings');
    const findings_list = document.getElementById('attachment-findings-list');
    
    // Show the attachment section
    attachment_section.classList.remove('hidden');
    
    // Clear previous findings
    findings_list.innerHTML = '';
    
    // Create finding cards for attachment
    attachment_findings.forEach((finding, index) => {
        const finding_card = document.createElement('div');
        finding_card.className = 'finding-item';
        finding_card.style.animationDelay = `${index * 0.1}s`;
        
        finding_card.innerHTML = `
            <div class="finding-header">
                <span class="finding-type">${finding.type.toUpperCase()}</span>
                <span class="finding-risk ${finding.risk.toLowerCase()}">${finding.risk}</span>
            </div>
            <div class="finding-value">${finding.value}</div>
            <div style="font-size: 12px; color: #7F8C8D; margin-top: 5px;">
                Found at: ${finding.location}
            </div>
        `;
        
        findings_list.appendChild(finding_card);
    });
}

function display_educational_content(education_info) {
    const education_content = document.getElementById('education-content');
    
    // Clear previous content
    education_content.innerHTML = '';
    
    // If no specific details, show generic privacy message
    if (!education_info.details || education_info.details.length === 0) {
        education_content.innerHTML = `
            <div class="education-item">
                <h3>🎉 Great job on privacy!</h3>
                <p>Your content looks safe to share. Keep being mindful about what information you post online!</p>
            </div>
        `;
        return;
    }
    
    // Create education cards for each risk type found
    education_info.details.forEach(detail => {
        const education_card = document.createElement('div');
        education_card.className = 'education-item';
        
        // Create tips HTML
        let tips_html = '';
        if (detail.tips && detail.tips.length > 0) {
            tips_html = `
                <div class="education-tips">
                    <h4>💡 Tips to Stay Safe:</h4>
                    <ul>
                        ${detail.tips.map(tip => `<li>${tip}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        education_card.innerHTML = `
            <h3>
                <span>${get_risk_emoji(detail.risk)}</span>
                ${detail.title}
            </h3>
            <p><strong>Why it's risky:</strong> ${detail.why_risky}</p>
            ${tips_html}
        `;
        
        education_content.appendChild(education_card);
    });
}

function get_risk_emoji(risk) {
    const emojis = {
        'Low': '✅',
        'Low-Medium': '⚠️',
        'Medium': '⚠️',
        'High': '🚨',
        'Critical': '🔴'
    };
    return emojis[risk] || '⚠️';
}

function show_masked_content() {
    // Show the masked version of the text
    const masked_card = document.getElementById('masked-text-card');
    const masked_display = document.getElementById('masked-text-display');
    
    if (current_scan_results) {
        masked_display.textContent = current_scan_results.masked_text;
        masked_card.classList.remove('hidden');
        
        // Update workflow step
        update_workflow_step(4); // Move to "Protect" step
        
        // Scroll to the masked content
        masked_card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

function copy_masked_text() {
    // Copy the masked text to clipboard
    const masked_text = current_scan_results.masked_text;
    
    navigator.clipboard.writeText(masked_text).then(() => {
        // Show success message
        const copy_button = document.getElementById('copy-btn');
        const original_text = copy_button.innerHTML;
        copy_button.innerHTML = '<span class="btn-icon">✅</span> Copied!';
        
        setTimeout(() => {
            copy_button.innerHTML = original_text;
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy text:', err);
        alert('Could not copy text. Please select and copy manually.');
    });
}

function show_social_preview() {
    // Show how the content looks on social media
    show_section('preview');
    update_workflow_step(5); // Move to "Preview" step
    
    // Get the masked text to display
    const text_to_preview = current_scan_results.masked_text;
    
    // Truncate text for different platforms
    const instagram_text = truncate_text(text_to_preview, 200);
    const twitter_text = truncate_text(text_to_preview, 280);
    const tiktok_text = truncate_text(text_to_preview, 150);
    
    // Update preview displays
    document.getElementById('instagram-text').textContent = instagram_text;
    document.getElementById('twitter-text').textContent = twitter_text;
    document.getElementById('tiktok-text').textContent = tiktok_text;
    
    // Scroll to preview section
    document.getElementById('preview-section').scrollIntoView({ behavior: 'smooth' });
}

function truncate_text(text, max_length) {
    // Cut text to fit platform limits
    if (text.length <= max_length) {
        return text;
    }
    return text.substring(0, max_length - 3) + '...';
}

function reset_app() {
    // Start over - clear everything
    document.getElementById('text-input').value = '';
    document.getElementById('file-upload').value = '';
    document.getElementById('file-name').textContent = 'Attach Document (PDF or Word)';
    
    current_scan_results = null;
    current_text = '';
    has_file_attached = false;
    attached_file_name = '';
    
    // Hide all sections except input
    show_section('input');
    update_workflow_step(1); // Back to step 1
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function show_section(section_name) {
    // Hide all sections
    document.getElementById('input-section').classList.add('hidden');
    document.getElementById('scanning-section').classList.add('hidden');
    document.getElementById('results-section').classList.add('hidden');
    document.getElementById('preview-section').classList.add('hidden');
    
    // Show the requested section
    if (section_name === 'input') {
        document.getElementById('input-section').classList.remove('hidden');
    } else if (section_name === 'scanning') {
        document.getElementById('scanning-section').classList.remove('hidden');
    } else if (section_name === 'results') {
        document.getElementById('results-section').classList.remove('hidden');
    } else if (section_name === 'preview') {
        document.getElementById('preview-section').classList.remove('hidden');
    }
}

function update_workflow_step(step_number) {
    // Update which step is active in the workflow
    for (let i = 1; i <= 5; i++) {
        const step_element = document.getElementById(`step-${i}`);
        if (i <= step_number) {
            step_element.classList.add('active');
        } else {
            step_element.classList.remove('active');
        }
    }
}

function sleep(milliseconds) {
    // Helper function to pause execution
    return new Promise(resolve => setTimeout(resolve, milliseconds));
}

// Log to console that app is ready
console.log('✅ TeenShare is ready to protect your privacy!');

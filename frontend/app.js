// Dynamic Prompt Template App - Main JavaScript File
class PromptTemplateApp {
    constructor() {
        this.currentTopic = '';
        this.currentPrompt = '';
        this.activeTab = 'gemini';
        this.charts = {};
        this.apiKeys = {
            gemini: '',
            youtube: ''
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.checkBackendHealth(); // Check if backend is ready
        this.loadQuickTopics();
        this.loadQuotaInfo();
        this.setDefaultTopic();
    }
    
    async checkBackendHealth() {
        try {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 5000);
            
            const response = await fetch('/api/health', {
                signal: controller.signal
            });
            
            clearTimeout(timeout);
            
            if (response.ok) {
                console.log('Backend is healthy and ready');
            } else {
                console.warn('Backend health check failed');
                this.showToast('Backend service may be starting up. Please wait...', 'warning');
            }
        } catch (error) {
            console.error('Backend health check error:', error);
            this.showToast('Connecting to backend... Please wait a moment.', 'warning');
        }
    }
    
    setupEventListeners() {
        // Topic input and generation
        document.getElementById('topicInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.generatePrompt();
            }
        });
        
        document.getElementById('generateBtn').addEventListener('click', () => {
            this.generatePrompt();
        });
        
        // Copy prompt functionality
        document.getElementById('copyPromptBtn').addEventListener('click', () => {
            this.copyPrompt();
        });
        
        // API key updates
        document.getElementById('updateKeysBtn').addEventListener('click', () => {
            this.updateApiKeys();
        });
        
        // Output generation buttons
        document.getElementById('queryGeminiBtn').addEventListener('click', () => {
            this.queryGemini();
        });
        
        document.getElementById('searchYouTubeBtn').addEventListener('click', () => {
            this.searchYouTube();
        });
        
        // Table controls
        document.getElementById('sortSelect')?.addEventListener('change', (e) => {
            this.sortVideos(e.target.value);
        });
        
        document.getElementById('filterSelect')?.addEventListener('change', (e) => {
            this.filterVideos(e.target.value);
        });
    }
    
    async setDefaultTopic() {
        document.getElementById('topicInput').value = 'Prompt Engineering';
        await this.generatePrompt();
    }
    
    async loadQuickTopics() {
        try {
            const response = await fetch('/api/topics/examples');
            const data = await response.json();
            
            if (data.success) {
                this.renderQuickTopics(data.data);
            }
        } catch (error) {
            console.error('Error loading quick topics:', error);
        }
    }
    
    renderQuickTopics(topics) {
        const container = document.getElementById('quickTopics');
        container.innerHTML = '';
        
        topics.forEach(topic => {
            const chip = document.createElement('span');
            chip.className = 'topic-chip';
            chip.textContent = topic;
            chip.addEventListener('click', () => {
                document.getElementById('topicInput').value = topic;
                this.generatePrompt();
            });
            container.appendChild(chip);
        });
    }
    
    async loadQuotaInfo() {
        try {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 10000); // 10 second timeout
            
            const response = await fetch('/api/quotas', {
                signal: controller.signal
            });
            
            clearTimeout(timeout);
            
            const data = await response.json();
            
            if (data.success) {
                this.renderQuotaCards(data.data);
            }
        } catch (error) {
            console.error('Error loading quota info:', error);
            // Don't show error toast for quota loading failure
        }
    }
    
    renderQuotaCards(quotas) {
        const container = document.getElementById('quotaCards');
        container.innerHTML = '';
        
        Object.entries(quotas).forEach(([service, quota]) => {
            const card = this.createQuotaCard(service, quota);
            container.appendChild(card);
        });
    }
    
    createQuotaCard(service, quota) {
        const percentage = Math.round(quota.percentage_used);
        const level = percentage < 30 ? 'low' : percentage < 70 ? 'medium' : 'high';
        
        const card = document.createElement('div');
        card.className = 'quota-card';
        
        card.innerHTML = `
            <div class="quota-header">
                <div class="quota-title">
                    <i class="fas ${service === 'gemini' ? 'fa-robot' : 'fab fa-youtube'}"></i>
                    ${quota.service}
                </div>
                <span class="quota-percentage ${level}">${percentage}%</span>
            </div>
            <div class="quota-bar">
                <div class="quota-fill ${level}" style="width: ${percentage}%"></div>
            </div>
            <div class="quota-details">
                <span>${quota.quota_used.toLocaleString()} used</span>
                <span>${quota.quota_remaining.toLocaleString()} remaining</span>
            </div>
        `;
        
        return card;
    }
    
    async generatePrompt() {
        const topic = document.getElementById('topicInput').value.trim();
        if (!topic) {
            this.showToast('Please enter a topic', 'warning');
            return;
        }
        
        this.currentTopic = topic;
        this.showLoading('Generating dynamic prompt template...');
        
        try {
            // Add timeout to prevent infinite loading
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 30000); // 30 second timeout
            
            const response = await fetch('/api/generate-prompt', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic }),
                signal: controller.signal
            });
            
            clearTimeout(timeout);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.currentPrompt = data.data.prompt;
                this.renderPrompt(data.data);
                this.enableOutputButtons();
                this.showToast('Prompt generated successfully!', 'success');
            } else {
                throw new Error('Failed to generate prompt');
            }
        } catch (error) {
            console.error('Error generating prompt:', error);
            if (error.name === 'AbortError') {
                this.showToast('Request timed out. Please try again.', 'error');
            } else {
                this.showToast(`Error: ${error.message}`, 'error');
            }
        } finally {
            this.hideLoading();
        }
    }
    
    renderPrompt(promptData) {
        const display = document.getElementById('promptDisplay');
        display.innerHTML = `<pre>${promptData.prompt}</pre>`;
        display.classList.add('fade-in');
        
        // Show metadata
        const metadata = document.getElementById('promptMetadata');
        metadata.style.display = 'block';
        metadata.innerHTML = `
            <div class="metadata-grid">
                <div class="metadata-item">
                    <span class="metadata-label">Topic</span>
                    <span class="metadata-value">${promptData.topic}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Word Count</span>
                    <span class="metadata-value">${promptData.word_count.toLocaleString()}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Character Count</span>
                    <span class="metadata-value">${promptData.character_count.toLocaleString()}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Generated</span>
                    <span class="metadata-value">${promptData.generated_at}</span>
                </div>
            </div>
            <div class="mt-lg">
                <strong>Focus Areas:</strong> ${promptData.focus_areas.join(', ')}
            </div>
        `;
    }
    
    async copyPrompt() {
        if (!this.currentPrompt) {
            this.showToast('No prompt to copy', 'warning');
            return;
        }
        
        try {
            await navigator.clipboard.writeText(this.currentPrompt);
            this.showToast('Prompt copied to clipboard!', 'success');
            
            // Visual feedback
            const btn = document.getElementById('copyPromptBtn');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
            setTimeout(() => {
                btn.innerHTML = originalText;
            }, 2000);
        } catch (error) {
            console.error('Error copying prompt:', error);
            this.showToast('Failed to copy prompt', 'error');
        }
    }
    
    async updateApiKeys() {
        const geminiKey = document.getElementById('geminiKey').value.trim();
        const youtubeKey = document.getElementById('youtubeKey').value.trim();
        
        if (!geminiKey && !youtubeKey) {
            this.showToast('Please enter at least one API key', 'warning');
            return;
        }
        
        this.showLoading('Updating API keys...');
        
        try {
            const response = await fetch('/api/update-keys', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    gemini_key: geminiKey || null,
                    youtube_key: youtubeKey || null
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                if (geminiKey) this.apiKeys.gemini = geminiKey;
                if (youtubeKey) this.apiKeys.youtube = youtubeKey;
                
                this.showToast('API keys updated successfully!', 'success');
                this.loadQuotaInfo(); // Refresh quota info
            } else {
                throw new Error('Failed to update API keys');
            }
        } catch (error) {
            console.error('Error updating API keys:', error);
            this.showToast('Error updating API keys', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    async queryGemini() {
        if (!this.currentPrompt) {
            this.showToast('Please generate a prompt first', 'warning');
            return;
        }
        
        this.showLoading('Querying Gemini AI...');
        
        try {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 60000); // 60 second timeout for AI
            
            const response = await fetch('/api/gemini/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic: this.currentTopic,
                    prompt: this.currentPrompt,
                    api_key: this.apiKeys.gemini || null
                }),
                signal: controller.signal
            });
            
            clearTimeout(timeout);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.renderGeminiResponse(data.data);
                this.showToast('Gemini response generated!', 'success');
                this.loadQuotaInfo(); // Refresh quota
            } else {
                throw new Error('Failed to query Gemini');
            }
        } catch (error) {
            console.error('Error querying Gemini:', error);
            if (error.name === 'AbortError') {
                this.showToast('Request timed out. Please try again.', 'error');
            } else {
                this.showToast(`Error: ${error.message}`, 'error');
            }
        } finally {
            this.hideLoading();
        }
    }
    
    renderGeminiResponse(responseData) {
        const output = document.getElementById('geminiOutput');
        
        if (responseData.error) {
            // Show demo response
            const demoData = responseData.demo_response;
            output.innerHTML = `
                <div class="gemini-response">
                    ${marked.parse(demoData.content)}
                </div>
                <div class="demo-note">
                    <i class="fas fa-info-circle"></i>
                    ${demoData.note}
                </div>
            `;
        } else {
            // Show actual AI response
            output.innerHTML = `
                <div class="gemini-response">
                    ${marked.parse(responseData.response)}
                </div>
                <div class="response-metadata" style="margin-top: 1rem; padding: 1rem; background: var(--bg-tertiary); border-radius: 0.5rem; font-size: 0.875rem;">
                    <strong>Model:</strong> ${responseData.model} | 
                    <strong>Tokens:</strong> ${responseData.tokens_used.toLocaleString()} | 
                    <strong>Generated:</strong> ${new Date(responseData.timestamp).toLocaleString()}
                </div>
            `;
        }
        
        output.classList.add('fade-in');
    }
    
    async searchYouTube() {
        if (!this.currentTopic) {
            this.showToast('Please generate a prompt first', 'warning');
            return;
        }
        
        this.showLoading('Searching YouTube videos...');
        
        try {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 60000); // 60 second timeout
            
            const response = await fetch('/api/youtube/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic: this.currentTopic,
                    api_key: this.apiKeys.youtube || null,
                    max_results: 60
                }),
                signal: controller.signal
            });
            
            clearTimeout(timeout);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.renderYouTubeResults(data.data);
                this.showAnalyticsSection();
                this.showVideoTableSection();
                this.showToast('YouTube analysis complete!', 'success');
                this.loadQuotaInfo(); // Refresh quota
            } else {
                throw new Error('Failed to search YouTube');
            }
        } catch (error) {
            console.error('Error searching YouTube:', error);
            if (error.name === 'AbortError') {
                this.showToast('Request timed out. Please try again.', 'error');
            } else {
                this.showToast(`Error: ${error.message}`, 'error');
            }
        } finally {
            this.hideLoading();
        }
    }
    
    renderYouTubeResults(youtubeData) {
        const content = document.getElementById('youtubeContent');
        const analytics = youtubeData.analytics;
        
        // Render stats overview
        content.innerHTML = `
            <div class="youtube-stats">
                <div class="stat-card">
                    <span class="stat-value">${youtubeData.total_found}</span>
                    <span class="stat-label">Videos Found</span>
                </div>
                <div class="stat-card">
                    <span class="stat-value">${analytics.total_views.toLocaleString()}</span>
                    <span class="stat-label">Total Views</span>
                </div>
                <div class="stat-card">
                    <span class="stat-value">${analytics.total_likes.toLocaleString()}</span>
                    <span class="stat-label">Total Likes</span>
                </div>
                <div class="stat-card">
                    <span class="stat-value">${analytics.total_watch_time_hours}h</span>
                    <span class="stat-label">Watch Time</span>
                </div>
                <div class="stat-card">
                    <span class="stat-value">${analytics.average_quality_score}</span>
                    <span class="stat-label">Avg Quality</span>
                </div>
            </div>
        `;
        
        if (youtubeData.is_demo) {
            content.innerHTML += `
                <div class="demo-note">
                    <i class="fas fa-info-circle"></i>
                    This is demo data. Provide your YouTube API key for real video analysis with 60 curated results.
                </div>
            `;
        }
        
        // Store data for charts and table
        this.youtubeData = youtubeData;
        this.renderCharts(analytics);
        this.renderVideoTable(youtubeData.videos);
        
        content.classList.add('fade-in');
    }
    
    renderCharts(analytics) {
        // Difficulty Distribution Pie Chart
        const difficultyCtx = document.getElementById('difficultyChart');
        if (difficultyCtx && analytics.difficulty_distribution) {
            this.charts.difficulty = new Chart(difficultyCtx, {
                type: 'pie',
                data: {
                    labels: Object.keys(analytics.difficulty_distribution),
                    datasets: [{
                        data: Object.values(analytics.difficulty_distribution),
                        backgroundColor: [
                            'rgba(16, 185, 129, 0.8)',
                            'rgba(245, 158, 11, 0.8)',
                            'rgba(239, 68, 68, 0.8)'
                        ],
                        borderColor: [
                            'rgb(16, 185, 129)',
                            'rgb(245, 158, 11)',
                            'rgb(239, 68, 68)'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        },
                        title: {
                            display: true,
                            text: 'Video Difficulty Levels'
                        }
                    }
                }
            });
        }
        
        // Top Channels Bar Chart
        const channelsCtx = document.getElementById('channelsChart');
        if (channelsCtx && analytics.top_channels) {
            const channels = analytics.top_channels.slice(0, 5);
            this.charts.channels = new Chart(channelsCtx, {
                type: 'bar',
                data: {
                    labels: channels.map(c => c.name.length > 15 ? c.name.substring(0, 15) + '...' : c.name),
                    datasets: [{
                        label: 'Video Count',
                        data: channels.map(c => c.count),
                        backgroundColor: 'rgba(99, 102, 241, 0.8)',
                        borderColor: 'rgb(99, 102, 241)',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Top Contributing Channels'
                        }
                    }
                }
            });
        }
    }
    
    renderVideoTable(videos) {
        const tbody = document.getElementById('videoTableBody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        videos.forEach((video, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <div class="video-info">
                        <img src="${video.thumbnail}" alt="Thumbnail" class="video-thumbnail" onerror="this.style.display='none'">
                        <div class="video-details">
                            <h4>${video.title}</h4>
                            <p>${video.description}</p>
                        </div>
                    </div>
                </td>
                <td>${video.channel_title}</td>
                <td>${video.duration_formatted}</td>
                <td>${video.view_count.toLocaleString()}</td>
                <td>${video.like_count.toLocaleString()}</td>
                <td>
                    <div class="quality-score">
                        <span>${video.quality_score}</span>
                        <div class="score-bar">
                            <div class="score-fill" style="width: ${Math.min(100, (video.quality_score / 10) * 100)}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="difficulty-badge ${video.difficulty_level.toLowerCase()}">
                        ${video.difficulty_level}
                    </span>
                </td>
                <td>
                    <a href="${video.url}" target="_blank" class="watch-btn">
                        <i class="fab fa-youtube"></i> Watch
                    </a>
                </td>
            `;
            tbody.appendChild(row);
        });
    }
    
    sortVideos(sortBy) {
        if (!this.youtubeData || !this.youtubeData.videos) return;
        
        const videos = [...this.youtubeData.videos];
        
        videos.sort((a, b) => {
            switch (sortBy) {
                case 'view_count':
                case 'like_count':
                case 'quality_score':
                    return b[sortBy] - a[sortBy];
                case 'published_at':
                    return new Date(b[sortBy]) - new Date(a[sortBy]);
                default:
                    return b.quality_score - a.quality_score;
            }
        });
        
        this.renderVideoTable(videos);
    }
    
    filterVideos(filterBy) {
        if (!this.youtubeData || !this.youtubeData.videos) return;
        
        let filteredVideos = this.youtubeData.videos;
        
        if (filterBy !== 'all') {
            filteredVideos = this.youtubeData.videos.filter(
                video => video.difficulty_level === filterBy
            );
        }
        
        this.renderVideoTable(filteredVideos);
    }
    
    enableOutputButtons() {
        document.getElementById('queryGeminiBtn').disabled = false;
        document.getElementById('searchYouTubeBtn').disabled = false;
    }
    
    showAnalyticsSection() {
        document.getElementById('analyticsSection').style.display = 'block';
        document.getElementById('analyticsSection').classList.add('fade-in');
    }
    
    showVideoTableSection() {
        document.getElementById('videoTableSection').style.display = 'block';
        document.getElementById('videoTableSection').classList.add('fade-in');
    }
    
    showLoading(message) {
        const overlay = document.getElementById('loadingOverlay');
        const text = document.getElementById('loadingText');
        text.textContent = message;
        overlay.classList.add('active');
    }
    
    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.classList.remove('active');
    }
    
    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        const icon = toast.querySelector('.toast-icon');
        const messageEl = toast.querySelector('.toast-message');
        
        // Set message
        messageEl.textContent = message;
        
        // Set type and icon
        toast.className = `toast ${type}`;
        switch (type) {
            case 'success':
                icon.className = 'toast-icon fas fa-check-circle success';
                break;
            case 'error':
                icon.className = 'toast-icon fas fa-exclamation-circle error';
                break;
            case 'warning':
                icon.className = 'toast-icon fas fa-exclamation-triangle warning';
                break;
            default:
                icon.className = 'toast-icon fas fa-info-circle';
        }
        
        // Show toast
        toast.classList.add('show');
        
        // Hide after 4 seconds
        setTimeout(() => {
            toast.classList.remove('show');
        }, 4000);
    }
}

// Tab switching functionality
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[onclick="switchTab('${tabName}')"]`).classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}Tab`).classList.add('active');
    
    app.activeTab = tabName;
}

// Section toggle functionality
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    const icon = section.previousElementSibling.querySelector('.toggle-icon');
    
    if (section.style.display === 'none') {
        section.style.display = 'block';
        icon.classList.add('rotated');
    } else {
        section.style.display = 'none';
        icon.classList.remove('rotated');
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new PromptTemplateApp();
});

// Handle window resize for charts
window.addEventListener('resize', () => {
    if (window.app && window.app.charts) {
        Object.values(window.app.charts).forEach(chart => {
            if (chart) chart.resize();
        });
    }
});
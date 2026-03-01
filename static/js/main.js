
        document.addEventListener('DOMContentLoaded', () => {
            const API_BASE_URL = 'http://127.0.0.1:8080';
            const USER_ID = 'user_1';

            // DOM Elements
            const chatWindow = document.getElementById('chat-window');
            const chatForm = document.getElementById('chat-form');
            const messageInput = document.getElementById('message-input');
            const sendButton = document.getElementById('send-button');
            const sessionList = document.getElementById('session-list');
            const generateProfileBtn = document.getElementById('generate-profile-btn');
            const getAggregationBtn = document.getElementById('get-aggregation-btn');
            const loadingOverlay = document.getElementById('loading-overlay');
            const sessionTitleEl = document.querySelector('#current-session-title .text');
            const userSummaryEl = document.getElementById('user-summary');
            const userTagsEl = document.getElementById('user-tags');
            const newChatBtn = document.getElementById('new-chat-btn');
            
            // Drawer Elements
            const drawerOverlay = document.getElementById('profile-drawer-overlay');
            const closeDrawerBtn = document.getElementById('close-drawer-btn');
            const drawerContent = document.getElementById('drawer-content');

            let currentSessionId = null;
            let radarChart = null; // Store chart instance

            // --- UTILITY FUNCTIONS ---
            const toggleGlobalLoading = (show) => {
                loadingOverlay.style.display = show ? 'flex' : 'none';
            };
            
            const openDrawer = (data) => {
                const renderField = (val) => (val && val !== '未知') ? val : '-';
                
                drawerContent.innerHTML = `
                    <div class="profile-section">
                        <h4><i class="fas fa-id-card"></i> 核心信息</h4>
                        <div class="profile-grid">
                            <div class="profile-item">
                                <div class="profile-item-label">用户昵称</div>
                                <div class="profile-item-value">${renderField(data.nickname)}</div>
                            </div>
                            <div class="profile-item">
                                <div class="profile-item-label">年龄</div>
                                <div class="profile-item-value">${renderField(data.age)} 岁</div>
                            </div>
                            <div class="profile-item">
                                <div class="profile-item-label">身高</div>
                                <div class="profile-item-value">${renderField(data.height)} cm</div>
                            </div>
                            <div class="profile-item">
                                <div class="profile-item-label">常驻城市</div>
                                <div class="profile-item-value">${renderField(data.city)}</div>
                            </div>
                            <div class="profile-item full-width-item">
                                <div class="profile-item-label">家乡/籍贯</div>
                                <div class="profile-item-value">${renderField(data.hometown)}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="profile-section">
                        <h4><i class="fas fa-briefcase"></i> 社会背景</h4>
                        <div class="profile-grid">
                            <div class="profile-item">
                                <div class="profile-item-label">职业行业</div>
                                <div class="profile-item-value">${renderField(data.occupation)}</div>
                            </div>
                            <div class="profile-item">
                                <div class="profile-item-label">年薪/收入</div>
                                <div class="profile-item-value">${renderField(data.income_level)}</div>
                            </div>
                            <div class="profile-item full-width-item">
                                <div class="profile-item-label">最高学历</div>
                                <div class="profile-item-value">${renderField(data.education)}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="profile-section">
                        <h4><i class="fas fa-coffee"></i> 生活习惯</h4>
                        <div class="profile-grid">
                            <div class="profile-item full-width-item">
                                <div class="profile-item-label">烟酒偏好</div>
                                <div class="profile-item-value">${renderField(data.smoking_drinking)}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="profile-section">
                        <h4><i class="fas fa-magic"></i> AI 匹配点评</h4>
                        <div class="profile-item full-width-item" style="background:#fff1f2; border-color:#fecdd3;">
                            <div class="profile-item-label" style="color:#e11d48; font-weight:bold;">综合匹配分：${data.score}</div>
                            <div class="profile-item-value" style="font-size:0.9rem; line-height:1.5; margin-top:0.5rem; color:#881337;">
                                ${data.match_reason}
                            </div>
                        </div>
                    </div>
                `;
                drawerOverlay.classList.add('active');
            };

            const closeDrawer = () => {
                drawerOverlay.classList.remove('active');
            };

            closeDrawerBtn.addEventListener('click', closeDrawer);
            drawerOverlay.addEventListener('click', (e) => {
                if (e.target === drawerOverlay) closeDrawer();
            });

            const apiFetch = async (endpoint, options = {}, useGlobalLoading = true) => {
                if (useGlobalLoading) toggleGlobalLoading(true);
                try {
                    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                        headers: {
                            'Content-Type': 'application/json',
                            ...options.headers,
                        },
                        ...options,
                    });
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    const result = await response.json();
                    if (result.code !== 0) {
                        throw new Error(result.message || 'API request failed');
                    }
                    return result.data;
                } catch (error) {
                    console.error('API Fetch Error:', error);
                    appendMessage(`API 请求失败: ${error.message}`, 'bot-message');
                    return null;
                } finally {
                    if (useGlobalLoading) toggleGlobalLoading(false);
                }
            };
            
            const appendMessage = (text, type, isHtml = false) => {
                let actualText = text;
                let cardsData = null;
                
                // Parse AI messages for <cards> JSON
                if (type === 'bot-message' && text.includes('<cards>')) {
                    const cardsMatch = text.match(/<cards>([\s\S]*?)<\/cards>/);
                    if (cardsMatch) {
                        try {
                            cardsData = JSON.parse(cardsMatch[1]);
                            actualText = text.replace(cardsMatch[0], '').trim();
                        } catch (e) {
                            console.error('Failed to parse cards JSON', e);
                        }
                    }
                }

                const messageElement = document.createElement('div');
                messageElement.classList.add('message', type);
                
                if (type === 'bot-message') {
                    const icon = document.createElement('i');
                    icon.classList.add('fas', 'fa-robot');
                    icon.style.marginRight = '8px';
                    icon.style.color = '#4f46e5';
                    
                    const contentSpan = document.createElement('span');
                    if(isHtml) {
                         const pre = document.createElement('pre');
                         pre.innerHTML = actualText;
                         contentSpan.appendChild(pre);
                    } else {
                        contentSpan.textContent = actualText;
                    }
                    
                    messageElement.appendChild(icon);
                    messageElement.appendChild(contentSpan);

                } else {
                    if (isHtml) {
                        const pre = document.createElement('pre');
                        pre.innerHTML = actualText;
                        messageElement.appendChild(pre);
                    } else {
                        messageElement.textContent = actualText;
                    }
                }

                chatWindow.appendChild(messageElement);

                // Render Cards Carousel if data exists
                if (cardsData && cardsData.length > 0) {
                    const carousel = document.createElement('div');
                    carousel.className = 'cards-carousel';
                    cardsData.forEach(card => {
                        const cardEl = document.createElement('div');
                        cardEl.className = 'match-card';
                        cardEl.innerHTML = `
                            <div class="card-header">
                                <span class="card-title"><i class="fas fa-user-circle" style="color: #9ca3af; margin-right: 4px;"></i> ${card.nickname || '匿名用户'}</span>
                                <span class="card-score"><i class="fas fa-heart"></i> ${card.score}</span>
                            </div>
                            <div class="card-tags">
                                <span class="card-tag"><i class="fas fa-birthday-cake"></i> ${card.age}岁</span>
                                <span class="card-tag"><i class="fas fa-map-marker-alt"></i> ${card.city || '未知'}</span>
                                <span class="card-tag"><i class="fas fa-briefcase"></i> ${card.occupation || '未知'}</span>
                            </div>
                            <div class="card-reason">${card.match_reason}</div>
                        `;
                        // Attach click event to open drawer
                        cardEl.addEventListener('click', () => openDrawer(card));
                        carousel.appendChild(cardEl);
                    });
                    chatWindow.appendChild(carousel);
                }

                // Use requestAnimationFrame to ensure the DOM has updated and calculated the new height of the carousel before scrolling.
                requestAnimationFrame(() => {
                    chatWindow.scrollTop = chatWindow.scrollHeight;
                });
            };
            
            // --- TYPING INDICATOR ---
            let typingElement = null;
            
            const showTypingIndicator = () => {
                if (typingElement) return;
                
                typingElement = document.createElement('div');
                typingElement.classList.add('message', 'bot-message');
                
                const icon = document.createElement('i');
                icon.classList.add('fas', 'fa-robot');
                icon.style.marginRight = '8px';
                icon.style.color = '#4f46e5';
                
                const indicator = document.createElement('div');
                indicator.classList.add('typing-indicator');
                indicator.innerHTML = '<span></span><span></span><span></span>';
                
                typingElement.appendChild(icon);
                typingElement.appendChild(indicator);
                
                chatWindow.appendChild(typingElement);
                chatWindow.scrollTop = chatWindow.scrollHeight;
            };
            
            const removeTypingIndicator = () => {
                if (typingElement && typingElement.parentNode) {
                    typingElement.parentNode.removeChild(typingElement);
                }
                typingElement = null;
            };

            // --- CHART FUNCTIONS ---
            const initChart = () => {
                const ctx = document.getElementById('radarChart').getContext('2d');
                const traitLabels = [
                    '外向性 (Extroversion)', 
                    '宜人性 (Agreeableness)', 
                    '尽责性 (Conscientiousness)', 
                    '神经质 (Neuroticism)', 
                    '开放性 (Openness)',
                    '支配性 (Dominance)', 
                    '同理心 (Empathy)', 
                    '冒险性 (Risk Taking)', 
                    '情绪稳定性 (Emotional Stability)', 
                    '自控力 (Self Control)'
                ];
                
                // Simplified labels for chart readability if needed, but let's try full first
                const simpleLabels = ['外向', '宜人', '尽责', '神经质', '开放', '支配', '同理', '冒险', '情绪', '自控'];

                radarChart = new Chart(ctx, {
                    type: 'radar',
                    data: {
                        labels: simpleLabels,
                        datasets: [{
                            label: '人格维度得分 (1-10)',
                            data: Array(10).fill(0), // Initial empty data
                            fill: true,
                            backgroundColor: 'rgba(79, 70, 229, 0.2)', // Primary color low opacity
                            borderColor: 'rgb(79, 70, 229)', // Primary color
                            pointBackgroundColor: 'rgb(79, 70, 229)',
                            pointBorderColor: '#fff',
                            pointHoverBackgroundColor: '#fff',
                            pointHoverBorderColor: 'rgb(79, 70, 229)'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        elements: {
                            line: { borderWidth: 3 }
                        },
                        scales: {
                            r: {
                                angleLines: {
                                    display: true,
                                    color: 'rgba(0, 0, 0, 0.1)'
                                },
                                suggestedMin: 0,
                                suggestedMax: 10,
                                ticks: {
                                    stepSize: 2,
                                    display: false // Hide numbers to make it cleaner? Or keep them.
                                },
                                pointLabels: {
                                    font: {
                                        size: 11,
                                        family: 'Inter'
                                    },
                                    color: '#4b5563'
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false // Title is redundant with sidebar header
                            }
                        }
                    }
                });
            };

            const updateChart = (data) => {
                if (!radarChart) initChart();
                
                // Map API data to chart order
                // Order in Model: extroversion, agreeableness, conscientiousness, neuroticism, openness, 
                // dominance, empathy, risk_taking, emotional_stability, self_control
                
                const newData = [
                    data.extroversion || 0,
                    data.agreeableness || 0,
                    data.conscientiousness || 0,
                    data.neuroticism || 0,
                    data.openness || 0,
                    data.dominance || 0,
                    data.empathy || 0,
                    data.risk_taking || 0,
                    data.emotional_stability || 0,
                    data.self_control || 0
                ];
                
                radarChart.data.datasets[0].data = newData;
                radarChart.update();
            };

            const contextMenu = document.getElementById('context-menu');
            const menuRenameBtn = document.getElementById('menu-rename');
            const menuDeleteBtn = document.getElementById('menu-delete');
            let activeMenuSessionId = null;

            // --- API ACTIONS ---
            const loadSessions = async () => {
                const sessions = await apiFetch('/getSessions', {
                    method: 'POST',
                    body: JSON.stringify({ user: USER_ID }),
                });


                sessionList.innerHTML = '';
                if (sessions && sessions.length > 0) {
                    sessions.forEach(session => {
                        const li = document.createElement('li');
                        const dateStr = new Date(session.created_at).toLocaleString('zh-CN', { month: 'numeric', day: 'numeric', hour: '2-digit', minute:'2-digit' });
                        
                        li.dataset.sessionId = session.id;
                        li.dataset.title = session.title;
                        li.classList.add('session-item'); // Add base class

                        const isSpecial = session.title.includes('交友助手');
                        if (isSpecial) {
                            li.classList.add('special');
                        }
                        
                        const menuHtml = isSpecial ? '' : '<button class="menu-btn" title="选项"><i class="fas fa-ellipsis-h"></i></button>';

                        li.innerHTML = `
                            <div class="session-item-content">
                                <div class="text-container" style="display:flex; flex-direction:column; overflow:hidden; flex-grow:1;">
                                    <span class="title-text" style="overflow:hidden; text-overflow:ellipsis;">${session.title}</span>
                                    <span style="font-size:0.75em; color:#9ca3af;">${dateStr}</span>
                                </div>
                                ${menuHtml}
                            </div>
                        `;
                        sessionList.appendChild(li);
                    });
                    
                    // Only auto-select first session if we are not in "New Session" mode initiated by user (though loadSessions is usually called on init)
                    if (currentSessionId === null && !document.querySelector('.new-session-placeholder')) {
                         const firstSessionId = sessions[0].id;
                         const firstSessionTitle = sessions[0].title;
                         await switchSession(firstSessionId, firstSessionTitle);
                    }
                } else {
                    enterNewSessionMode();
                }
            };
            
            // ... (keep updateSessionHeader, switchSession, enterNewSessionMode, etc.)

            // ... (keep existing listeners)

            // --- MENU HANDLERS ---
            
            // Hide menu on global click
            document.addEventListener('click', (e) => {
                if (!contextMenu.contains(e.target) && !e.target.closest('.menu-btn')) {
                    contextMenu.style.display = 'none';
                }
            });

            // Handle Menu Button Click
            sessionList.addEventListener('click', (e) => {
                const menuBtn = e.target.closest('.menu-btn');
                if (menuBtn) {
                    e.stopPropagation(); // Prevent switching session
                    const li = menuBtn.closest('li');
                    activeMenuSessionId = li.dataset.sessionId;
                    
                    const isSpecial = li.classList.contains('special');
                    
                    // Show/Hide Delete Button based on session type
                    if (isSpecial) {
                        menuDeleteBtn.style.display = 'none';
                    } else {
                        menuDeleteBtn.style.display = 'flex'; // Restore default display
                    }

                    const rect = menuBtn.getBoundingClientRect();
                    contextMenu.style.display = 'flex';
                    contextMenu.style.top = `${rect.bottom + window.scrollY}px`;
                    contextMenu.style.left = `${rect.right - 120 + window.scrollX}px`; // Align right edge roughly
                    return;
                }
                
                // Normal Session Switch
                const li = e.target.closest('li');
                if (li && li.dataset.sessionId && !e.target.closest('input')) { // Don't switch if clicking input
                    switchSession(parseInt(li.dataset.sessionId, 10), li.dataset.title);
                }
            });

            // Rename Logic
            menuRenameBtn.addEventListener('click', () => {
                contextMenu.style.display = 'none';
                if (!activeMenuSessionId) return;
                
                const li = document.querySelector(`li[data-session-id="${activeMenuSessionId}"]`);
                if (!li) return;
                
                const titleSpan = li.querySelector('.title-text');
                const originalTitle = titleSpan.textContent;
                
                const input = document.createElement('input');
                input.type = 'text';
                input.value = originalTitle;
                input.classList.add('session-title-edit');
                
                // Replace span with input
                titleSpan.replaceWith(input);
                input.focus();
                
                const saveRename = async () => {
                    const newTitle = input.value.trim();
                    if (newTitle && newTitle !== originalTitle) {
                        const success = await apiFetch('/renameSession', {
                            method: 'POST',
                            body: JSON.stringify({ session_id: parseInt(activeMenuSessionId), title: newTitle })
                        });
                        
                        if (success) {
                             li.dataset.title = newTitle;
                             if (parseInt(activeMenuSessionId) === currentSessionId) {
                                 updateSessionHeader(newTitle);
                             }
                        }
                    }
                    // Revert UI (whether saved or not, show text again)
                    // If saved, use newTitle, else use original
                    const displayTitle = (input.value.trim() && input.value.trim() !== originalTitle) ? input.value.trim() : originalTitle;
                    
                    const newSpan = document.createElement('span');
                    newSpan.classList.add('title-text');
                    newSpan.style.overflow = 'hidden';
                    newSpan.style.textOverflow = 'ellipsis';
                    newSpan.textContent = displayTitle;
                    
                    if (input.parentNode) {
                        input.replaceWith(newSpan);
                    }
                };
                
                input.addEventListener('blur', saveRename);
                input.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        input.blur();
                    }
                });
            });

            // --- MODAL LOGIC ---
            const deleteModal = document.getElementById('delete-modal');
            const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
            const cancelDeleteBtn = document.getElementById('cancel-delete-btn');
            let sessionToDelete = null;

            const showDeleteModal = (sessionId) => {
                sessionToDelete = sessionId;
                deleteModal.classList.add('active');
            };

            const hideDeleteModal = () => {
                deleteModal.classList.remove('active');
                setTimeout(() => { sessionToDelete = null; }, 200); // Clear after animation
            };

            // Close modal on outside click
            deleteModal.addEventListener('click', (e) => {
                if (e.target === deleteModal) hideDeleteModal();
            });

            cancelDeleteBtn.addEventListener('click', hideDeleteModal);

            confirmDeleteBtn.addEventListener('click', async () => {
                if (!sessionToDelete) return;
                
                const sessionId = sessionToDelete; 
                hideDeleteModal(); 

                const success = await apiFetch('/deleteSession', {
                    method: 'POST',
                    body: JSON.stringify({ session_id: parseInt(sessionId) })
                });
                
                if (success) {
                    const li = document.querySelector(`li[data-session-id="${sessionId}"]`);
                    if (li) li.remove();
                    
                    if (parseInt(sessionId) === currentSessionId) {
                        const first = sessionList.querySelector('li');
                        if (first) {
                            switchSession(parseInt(first.dataset.sessionId), first.dataset.title);
                        } else {
                            enterNewSessionMode();
                        }
                    }
                }
            });

            // Delete Logic (Menu Click)
            menuDeleteBtn.addEventListener('click', () => {
                contextMenu.style.display = 'none';
                if (!activeMenuSessionId) return;
                
                showDeleteModal(activeMenuSessionId);
            });

            const updateSessionHeader = (title) => {
                sessionTitleEl.textContent = title || '未命名会话';
            };

            const switchSession = async (sessionId, title) => {
                if (currentSessionId === sessionId) return;
                currentSessionId = sessionId;
                
                const chatPanel = document.querySelector('.chat-panel');
                chatPanel.classList.remove('special-mode');

                document.querySelectorAll('#session-list li').forEach(li => {
                    if (li.dataset.sessionId == sessionId) {
                         li.classList.add('active');
                         if(!title) title = li.dataset.title || li.querySelector('span').textContent;
                         
                         if (li.classList.contains('special')) {
                             chatPanel.classList.add('special-mode');
                         }
                    } else {
                         li.classList.remove('active');
                    }
                });
                
                updateSessionHeader(title);
                chatWindow.innerHTML = ''; 
                
                const chatHistory = await apiFetch(`/getChats/${sessionId}`);
                
                if (chatHistory && chatHistory.chats) {
                    chatHistory.chats.forEach(chat => {
                        if (chat.type === 0) {
                            appendMessage(chat.content, 'user-message', false);
                        } else {
                            appendMessage(chat.content, 'bot-message', true);
                        }
                    });
                } else {
                     const welcome = document.createElement('div');
                     welcome.classList.add('bot-message', 'message');
                     welcome.innerHTML = '<i class="fas fa-robot" style="margin-right: 8px; color: #4f46e5;"></i> <span>我是 PeopleScope AI，请问有什么可以帮您？</span>';
                     chatWindow.appendChild(welcome);
                }
                enableChatInput();
            };
            
            const enterNewSessionMode = () => {
                currentSessionId = null; // Reset to null for new session
                document.querySelectorAll('#session-list li').forEach(li => li.classList.remove('active'));
                
                updateSessionHeader('新建会话');
                chatWindow.innerHTML = '';
                
                const welcome = document.createElement('div');
                welcome.classList.add('bot-message', 'message');
                welcome.innerHTML = '<i class="fas fa-robot" style="margin-right: 8px; color: #4f46e5;"></i> <span>你好！我是 PeopleScope AI。请在下方输入您的问题以开始新的对话。</span>';
                chatWindow.appendChild(welcome);
                
                enableChatInput();
                messageInput.focus();
            };

            const loadUserProfile = async () => {
                // Fetch Aggregation (Radar + Summary)
                const aggregation = await apiFetch('/getAggregation', {
                    method: 'POST',
                    body: JSON.stringify({ user: USER_ID })
                });

                if (aggregation) {
                    // Update Chart
                    updateChart(aggregation);
                    
                    // Update Summary
                    if (aggregation.summary) {
                        userSummaryEl.textContent = aggregation.summary;
                        userSummaryEl.classList.remove('empty-state');
                    } else {
                        userSummaryEl.textContent = "暂无文字总结，请点击生成按钮进行分析。";
                        userSummaryEl.classList.add('empty-state');
                    }
                }

                // Fetch User Tags
                const userData = await apiFetch('/getUser', {
                    method: 'POST',
                    body: JSON.stringify({ user: USER_ID })
                }, false); // don't block for this one

                if (userData && userData.tags) {
                    displayTags(userData.tags);
                }
            };

            const displayTags = (tags) => {
                userTagsEl.innerHTML = '';
                
                if (tags.topic && Array.isArray(tags.topic) && tags.topic.length > 0) {
                    const topicRow = document.createElement('div');
                    topicRow.classList.add('tag-row');
                    topicRow.innerHTML = `
                        <div class="tag-label">关注主题 (Topics)</div>
                        <div class="tag-container" id="topic-container"></div>
                    `;
                    userTagsEl.appendChild(topicRow);
                    const container = topicRow.querySelector('#topic-container');
                    tags.topic.forEach(topic => {
                        const span = document.createElement('span');
                        span.classList.add('tag', 'tag-topic');
                        span.textContent = topic;
                        container.appendChild(span);
                    });
                }
                
                if (tags.style && Array.isArray(tags.style) && tags.style.length > 0) {
                    const styleRow = document.createElement('div');
                    styleRow.classList.add('tag-row');
                    styleRow.innerHTML = `
                        <div class="tag-label">交流风格 (Style)</div>
                        <div class="tag-container" id="style-container"></div>
                    `;
                    userTagsEl.appendChild(styleRow);
                    const container = styleRow.querySelector('#style-container');
                    tags.style.forEach(style => {
                        const span = document.createElement('span');
                        span.classList.add('tag', 'tag-style');
                        span.textContent = style;
                        container.appendChild(span);
                    });
                }
            };
            
            const enableChatInput = () => {
                messageInput.disabled = false;
                sendButton.disabled = false;
                messageInput.placeholder = `发送消息...`;
                messageInput.focus();
            }

            // --- LISTENERS ---
            chatForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const message = messageInput.value.trim();
                // Allow submit if message exists, even if currentSessionId is null (for creation)
                if (!message) return;

                appendMessage(message, 'user-message');
                messageInput.value = '';
                showTypingIndicator();

                if (currentSessionId === null) {
                    // Create New Session
                    const newSessionId = await apiFetch('/createSession', {
                        method: 'POST',
                        body: JSON.stringify({
                            user: USER_ID,
                            message: message
                        })
                    }, false); // don't block global loading to keep typing indicator
                    
                    if (newSessionId) {
                        currentSessionId = newSessionId;
                        // Reload session list to show new session
                        await loadSessions(); 
                        
                        // Update header title and active state for the new session
                        const newSessionLi = document.querySelector(`#session-list li[data-session-id="${newSessionId}"]`);
                        if (newSessionLi) {
                            const newTitle = newSessionLi.dataset.title;
                            updateSessionHeader(newTitle);
                            document.querySelectorAll('#session-list li').forEach(li => li.classList.remove('active'));
                            newSessionLi.classList.add('active');
                        }

                        // Switch to new session (visually update active state and load chats including the AI response generated by backend)
                        // Note: Backend generates response during creation, so we need to fetch chats now.
                        
                        // We need to fetch chats to get the AI response that was generated
                        const chatHistory = await apiFetch(`/getChats/${newSessionId}`, {}, false);
                        
                        removeTypingIndicator();
                        // Clear chat window to avoid duplicate user message (since we just appended it manually), 
                        // OR just append the LAST message (AI response). 
                        // Better to reload cleanly or just append the AI response if we trust the order.
                        
                        // Current approach: user msg appended manually. Backend has User Msg + AI Msg.
                        // If we fetch chats, we get both.
                        // Let's just remove typing indicator and append the AI response from the fetched list (it should be the last one).
                        
                        if (chatHistory && chatHistory.chats && chatHistory.chats.length > 0) {
                            const lastChat = chatHistory.chats[chatHistory.chats.length - 1];
                            if (lastChat.type === 1) { // Ensure it is AI response
                                appendMessage(lastChat.content, 'bot-message', true);
                            }
                        }
                    } else {
                        removeTypingIndicator();
                        appendMessage('会话创建失败，请重试。', 'bot-message');
                    }
                    
                } else {
                    // Existing Session Chat
                    const currentLi = document.querySelector(`li[data-session-id="${currentSessionId}"]`);
                    const isSpecial = currentLi && currentLi.classList.contains('special');
                    const endpoint = isSpecial ? '/info_chat' : '/chat';

                    const response = await apiFetch(endpoint, {
                        method: 'POST',
                        body: JSON.stringify({
                            user: USER_ID,
                            session_id: parseInt(currentSessionId, 10),
                            message: message
                        })
                    }, false); 
                    
                    removeTypingIndicator();
                    if (response) {
                        appendMessage(response, 'bot-message', true);
                    }
                }
            });

            
            newChatBtn.addEventListener('click', () => {
                enterNewSessionMode();
            });

            generateProfileBtn.addEventListener('click', async () => {
                const result = await apiFetch('/generateUserTags', {
                    method: 'POST',
                    body: JSON.stringify({ user: USER_ID })
                });
                if (result) {
                    appendMessage('已请求生成/更新用户画像。请稍等片刻后点击“刷新画像数据”查看最新雷达图和总结。', 'bot-message');
                }
            });

            getAggregationBtn.addEventListener('click', loadUserProfile);

            // --- INIT ---
            const initialize = async () => {
                initChart(); // Init chart empty
                await loadSessions();
                await loadUserProfile();
            };

            initialize();
        });
    
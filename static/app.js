/**
 * SpendWise — Professional Minimalist Single Page Application
 * Clean, reactive, production-grade JavaScript client
 */

(() => {
  'use strict';

  // ---------------------------------------------------------------------------
  // State Management
  // ---------------------------------------------------------------------------
  const savedCurrency = localStorage.getItem('spendwise_currency');
  const state = {
    expenses: [],
    categories: [],
    currency: (savedCurrency && savedCurrency !== '$') ? savedCurrency : '₹',
    theme: localStorage.getItem('spendwise_theme') || 'dark',
    editingId: null,
    searchQuery: '',
    selectedCategoryFilter: '',
    startDateFilter: '',
    endDateFilter: '',
    selectedYear: new Date().getFullYear(),
    selectedMonth: new Date().getMonth() + 1,
  };

  // Category emoji and styling map
  const CATEGORY_MAP = {
    food: { icon: '🍔', name: 'Food' },
    groceries: { icon: '🛒', name: 'Groceries' },
    transport: { icon: '🚗', name: 'Transport' },
    travel: { icon: '✈️', name: 'Travel' },
    shopping: { icon: '🛍️', name: 'Shopping' },
    utilities: { icon: '💡', name: 'Utilities' },
    housing: { icon: '🏠', name: 'Housing' },
    rent: { icon: '🏠', name: 'Rent' },
    entertainment: { icon: '🎬', name: 'Entertainment' },
    health: { icon: '💊', name: 'Health' },
    healthcare: { icon: '💊', name: 'Healthcare' },
    education: { icon: '📚', name: 'Education' },
    bills: { icon: '📄', name: 'Bills' },
    other: { icon: '📁', name: 'Other' },
  };

  function getCategoryInfo(rawCat) {
    const key = (rawCat || '').toLowerCase().trim();
    if (CATEGORY_MAP[key]) return CATEGORY_MAP[key];
    return { icon: '🏷️', name: rawCat || 'General' };
  }

  // ---------------------------------------------------------------------------
  // DOM Elements
  // ---------------------------------------------------------------------------
  const dom = {
    // Header & Controls
    themeToggleBtn: document.getElementById('themeToggleBtn'),
    currencySelect: document.getElementById('currencySelect'),
    openAddModalBtn: document.getElementById('openAddModalBtn'),
    apiStatusBadge: document.getElementById('apiStatusBadge'),

    // Stats
    statTotalSpend: document.getElementById('statTotalSpend'),
    statExpenseCount: document.getElementById('statExpenseCount'),
    statTopCategory: document.getElementById('statTopCategory'),
    statTopCategoryAmount: document.getElementById('statTopCategoryAmount'),
    statMonthlySpend: document.getElementById('statMonthlySpend'),
    statMonthlySubtext: document.getElementById('statMonthlySubtext'),

    // Category breakdown
    categoriesList: document.getElementById('categoriesList'),
    categoryCountBadge: document.getElementById('categoryCountBadge'),

    // Monthly explorer
    monthlyYearSelect: document.getElementById('monthlyYearSelect'),
    monthlyMonthSelect: document.getElementById('monthlyMonthSelect'),
    monthlyResultAmount: document.getElementById('monthlyResultAmount'),
    monthlyResultCount: document.getElementById('monthlyResultCount'),

    // Filter toolbar
    searchInput: document.getElementById('searchInput'),
    clearSearchBtn: document.getElementById('clearSearchBtn'),
    categoryFilter: document.getElementById('categoryFilter'),
    startDateFilter: document.getElementById('startDateFilter'),
    endDateFilter: document.getElementById('endDateFilter'),
    resetFiltersBtn: document.getElementById('resetFiltersBtn'),

    // Table & States
    expensesTableBody: document.getElementById('expensesTableBody'),
    emptyState: document.getElementById('emptyState'),
    emptyAddBtn: document.getElementById('emptyAddBtn'),
    loadingState: document.getElementById('loadingState'),

    // Modal
    expenseModal: document.getElementById('expenseModal'),
    modalTitle: document.getElementById('modalTitle'),
    closeModalBtn: document.getElementById('closeModalBtn'),
    cancelModalBtn: document.getElementById('cancelModalBtn'),
    expenseForm: document.getElementById('expenseForm'),
    expenseIdInput: document.getElementById('expenseIdInput'),
    formTitle: document.getElementById('formTitle'),
    formAmount: document.getElementById('formAmount'),
    formCurrencyPrefix: document.getElementById('formCurrencyPrefix'),
    formDate: document.getElementById('formDate'),
    formCategory: document.getElementById('formCategory'),
    formNote: document.getElementById('formNote'),
    categoryChips: document.getElementById('categoryChips'),
    saveBtnText: document.getElementById('saveBtnText'),

    // Error messages
    titleError: document.getElementById('titleError'),
    amountError: document.getElementById('amountError'),
    dateError: document.getElementById('dateError'),
    categoryError: document.getElementById('categoryError'),

    // Toast
    toastContainer: document.getElementById('toastContainer'),
  };

  // ---------------------------------------------------------------------------
  // Utilities
  // ---------------------------------------------------------------------------
  function formatMoney(amount) {
    const num = Number(amount) || 0;
    const locale = state.currency === '₹' ? 'en-IN' : undefined;
    return `${state.currency}${num.toLocaleString(locale, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  }

  function formatDate(isoDate) {
    if (!isoDate) return '—';
    try {
      const [year, month, day] = isoDate.split('-');
      const d = new Date(year, month - 1, day);
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    } catch {
      return isoDate;
    }
  }

  function getTodayIso() {
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  }

  function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <span>${type === 'success' ? '✓' : '✕'}</span>
      <span>${message}</span>
    `;
    dom.toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.animation = 'toastOut 0.25s forwards';
      setTimeout(() => toast.remove(), 250);
    }, 3500);
  }

  // ---------------------------------------------------------------------------
  // API Calls
  // ---------------------------------------------------------------------------
  async function apiFetch(endpoint, options = {}) {
    try {
      const response = await fetch(endpoint, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        let message = errorData.detail || 'Request failed';
        if (Array.isArray(errorData.errors)) {
          message = errorData.errors.map(e => `${e.field}: ${e.message}`).join(', ');
        }
        throw new Error(message);
      }

      return await response.json();
    } catch (err) {
      console.error(`API Error on ${endpoint}:`, err);
      throw err;
    }
  }

  // ---------------------------------------------------------------------------
  // Data Loaders
  // ---------------------------------------------------------------------------
  async function loadAllData() {
    dom.loadingState.style.display = 'flex';
    try {
      await Promise.all([
        loadExpenses(),
        loadSummaries(),
        loadMonthlySummary(),
      ]);
    } catch (err) {
      showToast('Could not load expense data: ' + err.message, 'error');
    } finally {
      dom.loadingState.style.display = 'none';
    }
  }

  async function loadExpenses() {
    const params = new URLSearchParams();
    if (state.selectedCategoryFilter) params.append('category', state.selectedCategoryFilter);
    if (state.startDateFilter) params.append('start_date', state.startDateFilter);
    if (state.endDateFilter) params.append('end_date', state.endDateFilter);

    const queryString = params.toString() ? `?${params.toString()}` : '';
    state.expenses = await apiFetch(`/expenses${queryString}`);
    renderExpensesTable();
  }

  async function loadSummaries() {
    const [overall, categoryData] = await Promise.all([
      apiFetch('/summary'),
      apiFetch('/summary/category'),
    ]);

    // Top metrics
    dom.statTotalSpend.textContent = formatMoney(overall.total_amount);
    dom.statExpenseCount.textContent = `${overall.total_count} transaction${overall.total_count === 1 ? '' : 's'} recorded`;

    // Category breakdown
    state.categories = categoryData.categories || [];
    renderCategories(overall.total_amount);

    // Top Category stat
    if (state.categories.length > 0) {
      const top = state.categories[0];
      const info = getCategoryInfo(top.category);
      dom.statTopCategory.textContent = `${info.icon} ${top.category}`;
      dom.statTopCategoryAmount.textContent = `${formatMoney(top.total_amount)} (${top.count} txns)`;
    } else {
      dom.statTopCategory.textContent = '—';
      dom.statTopCategoryAmount.textContent = 'No data yet';
    }
  }

  async function loadMonthlySummary() {
    try {
      const res = await apiFetch(`/summary/monthly?year=${state.selectedYear}&month=${state.selectedMonth}`);
      dom.monthlyResultAmount.textContent = formatMoney(res.total_amount);
      dom.monthlyResultCount.textContent = `${res.total_count} transaction${res.total_count === 1 ? '' : 's'}`;

      const now = new Date();
      if (state.selectedYear === now.getFullYear() && state.selectedMonth === (now.getMonth() + 1)) {
        dom.statMonthlySpend.textContent = formatMoney(res.total_amount);
        dom.statMonthlySubtext.textContent = `Spent in ${now.toLocaleString(undefined, { month: 'long' })}`;
      }
    } catch (err) {
      console.error(err);
    }
  }

  // ---------------------------------------------------------------------------
  // Renderers
  // ---------------------------------------------------------------------------
  function renderExpensesTable() {
    const q = state.searchQuery.toLowerCase().trim();
    const filtered = state.expenses.filter(item => {
      if (!q) return true;
      return (
        item.title.toLowerCase().includes(q) ||
        (item.note && item.note.toLowerCase().includes(q)) ||
        item.category.toLowerCase().includes(q)
      );
    });

    dom.expensesTableBody.innerHTML = '';

    if (filtered.length === 0) {
      dom.emptyState.style.display = 'flex';
      return;
    }

    dom.emptyState.style.display = 'none';

    filtered.forEach(exp => {
      const tr = document.createElement('tr');
      const catInfo = getCategoryInfo(exp.category);

      tr.innerHTML = `
        <td class="expense-date-badge">${formatDate(exp.date)}</td>
        <td>
          <div class="expense-title-group">
            <span class="expense-title">${escapeHtml(exp.title)}</span>
            ${exp.note ? `<span class="expense-note">${escapeHtml(exp.note)}</span>` : ''}
          </div>
        </td>
        <td>
          <span class="cat-badge">
            <span>${catInfo.icon}</span>
            <span>${escapeHtml(exp.category)}</span>
          </span>
        </td>
        <td class="text-right expense-amount-cell font-mono">${formatMoney(exp.amount)}</td>
        <td class="text-right">
          <div class="action-buttons">
            <button class="icon-btn edit-btn" data-id="${exp.id}" title="Edit Expense" aria-label="Edit">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/></svg>
            </button>
            <button class="icon-btn delete-btn" data-id="${exp.id}" title="Delete Expense" aria-label="Delete">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
            </button>
          </div>
        </td>
      `;
      dom.expensesTableBody.appendChild(tr);
    });

    // Wire action buttons
    dom.expensesTableBody.querySelectorAll('.edit-btn').forEach(btn => {
      btn.addEventListener('click', () => handleEdit(Number(btn.dataset.id)));
    });
    dom.expensesTableBody.querySelectorAll('.delete-btn').forEach(btn => {
      btn.addEventListener('click', () => handleDelete(Number(btn.dataset.id)));
    });
  }

  function renderCategories(overallTotal) {
    dom.categoryCountBadge.textContent = `${state.categories.length} Categor${state.categories.length === 1 ? 'y' : 'ies'}`;
    
    // Update filter dropdown options dynamically
    const currentFilterVal = dom.categoryFilter.value;
    dom.categoryFilter.innerHTML = '<option value="">All Categories</option>';
    state.categories.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.category;
      opt.textContent = `${c.category} (${c.count})`;
      if (c.category === currentFilterVal) opt.selected = true;
      dom.categoryFilter.appendChild(opt);
    });

    dom.categoriesList.innerHTML = '';
    if (state.categories.length === 0) {
      dom.categoriesList.innerHTML = '<div class="empty-state-sm">No expenses recorded yet.</div>';
      return;
    }

    state.categories.forEach(item => {
      const pct = overallTotal > 0 ? ((item.total_amount / overallTotal) * 100).toFixed(1) : 0;
      const info = getCategoryInfo(item.category);

      const div = document.createElement('div');
      div.className = 'category-row';
      div.innerHTML = `
        <div class="category-row-meta">
          <div class="category-name-wrap">
            <span>${info.icon}</span>
            <span>${escapeHtml(item.category)}</span>
          </div>
          <div class="category-stat-wrap">
            <span class="category-pct">${pct}%</span>
            <span class="category-amount font-mono">${formatMoney(item.total_amount)}</span>
          </div>
        </div>
        <div class="progress-track">
          <div class="progress-fill" style="width: ${pct}%"></div>
        </div>
      `;
      dom.categoriesList.appendChild(div);
    });
  }

  function populateYearSelector() {
    dom.monthlyYearSelect.innerHTML = '';
    const currentYear = new Date().getFullYear();
    for (let y = currentYear - 4; y <= currentYear + 2; y++) {
      const opt = document.createElement('option');
      opt.value = y;
      opt.textContent = y;
      if (y === state.selectedYear) opt.selected = true;
      dom.monthlyYearSelect.appendChild(opt);
    }
    dom.monthlyMonthSelect.value = state.selectedMonth;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // ---------------------------------------------------------------------------
  // Modal & Form Handlers
  // ---------------------------------------------------------------------------
  function openModal(isEdit = false, item = null) {
    clearFormErrors();
    dom.expenseForm.reset();

    if (isEdit && item) {
      state.editingId = item.id;
      dom.modalTitle.textContent = 'Edit Expense';
      dom.saveBtnText.textContent = 'Update Expense';
      dom.expenseIdInput.value = item.id;
      dom.formTitle.value = item.title;
      dom.formAmount.value = item.amount;
      dom.formDate.value = item.date;
      dom.formCategory.value = item.category;
      dom.formNote.value = item.note || '';
    } else {
      state.editingId = null;
      dom.modalTitle.textContent = 'New Expense';
      dom.saveBtnText.textContent = 'Save Expense';
      dom.expenseIdInput.value = '';
      dom.formDate.value = getTodayIso();
    }

    // Highlight chip if matching
    updateChipSelection(dom.formCategory.value);

    dom.formCurrencyPrefix.textContent = state.currency;
    dom.expenseModal.classList.add('open');
    dom.expenseModal.setAttribute('aria-hidden', 'false');
    dom.formTitle.focus();
  }

  function closeModal() {
    dom.expenseModal.classList.remove('open');
    dom.expenseModal.setAttribute('aria-hidden', 'true');
    state.editingId = null;
  }

  function updateChipSelection(categoryValue) {
    dom.categoryChips.querySelectorAll('.chip').forEach(chip => {
      if (chip.dataset.cat.toLowerCase() === (categoryValue || '').toLowerCase().trim()) {
        chip.classList.add('active');
      } else {
        chip.classList.remove('active');
      }
    });
  }

  function clearFormErrors() {
    dom.titleError.textContent = '';
    dom.amountError.textContent = '';
    dom.dateError.textContent = '';
    dom.categoryError.textContent = '';
  }

  async function handleFormSubmit(e) {
    e.preventDefault();
    clearFormErrors();

    const title = dom.formTitle.value.trim();
    const amount = parseFloat(dom.formAmount.value);
    const date = dom.formDate.value;
    const category = dom.formCategory.value.trim();
    const note = dom.formNote.value.trim() || null;

    let hasError = false;
    if (!title) {
      dom.titleError.textContent = 'Please enter a title.';
      hasError = true;
    }
    if (isNaN(amount) || amount <= 0) {
      dom.amountError.textContent = 'Amount must be greater than zero.';
      hasError = true;
    }
    if (!date) {
      dom.dateError.textContent = 'Please select a date.';
      hasError = true;
    }
    if (!category) {
      dom.categoryError.textContent = 'Please specify a category.';
      hasError = true;
    }

    if (hasError) return;

    const payload = { title, amount, category, date, note };

    try {
      if (state.editingId) {
        await apiFetch(`/expenses/${state.editingId}`, {
          method: 'PUT',
          body: JSON.stringify(payload),
        });
        showToast('Expense updated successfully');
      } else {
        await apiFetch('/expenses', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
        showToast('Expense created successfully');
      }

      closeModal();
      await loadAllData();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  function handleEdit(id) {
    const item = state.expenses.find(e => e.id === id);
    if (!item) return;
    openModal(true, item);
  }

  async function handleDelete(id) {
    const item = state.expenses.find(e => e.id === id);
    const title = item ? item.title : 'this expense';
    if (!confirm(`Are you sure you want to delete "${title}"?`)) {
      return;
    }

    try {
      await apiFetch(`/expenses/${id}`, { method: 'DELETE' });
      showToast('Expense deleted');
      await loadAllData();
    } catch (err) {
      showToast('Failed to delete expense: ' + err.message, 'error');
    }
  }

  // ---------------------------------------------------------------------------
  // Theme & Preferences
  // ---------------------------------------------------------------------------
  function applyTheme(theme) {
    state.theme = theme;
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem('spendwise_theme', theme);
  }

  function toggleTheme() {
    const nextTheme = state.theme === 'dark' ? 'light' : 'dark';
    applyTheme(nextTheme);
  }

  function applyCurrency(curr) {
    state.currency = curr;
    localStorage.setItem('spendwise_currency', curr);
    dom.currencySelect.value = curr;
    dom.formCurrencyPrefix.textContent = curr;
    renderExpensesTable();
    loadSummaries();
    loadMonthlySummary();
  }

  // ---------------------------------------------------------------------------
  // Event Listeners Initialization
  // ---------------------------------------------------------------------------
  function setupEventListeners() {
    // Theme toggle
    dom.themeToggleBtn.addEventListener('click', toggleTheme);

    // Currency selector
    dom.currencySelect.addEventListener('change', (e) => {
      applyCurrency(e.target.value);
    });

    // Modals
    dom.openAddModalBtn.addEventListener('click', () => openModal(false));
    dom.emptyAddBtn.addEventListener('click', () => openModal(false));
    dom.closeModalBtn.addEventListener('click', closeModal);
    dom.cancelModalBtn.addEventListener('click', closeModal);
    dom.expenseForm.addEventListener('submit', handleFormSubmit);

    // Click outside modal dialog to dismiss
    dom.expenseModal.addEventListener('click', (e) => {
      if (e.target === dom.expenseModal) closeModal();
    });

    // Keyboard shortcuts: ESC closes modal, '+' or 'N' opens modal
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && dom.expenseModal.classList.contains('open')) {
        closeModal();
      }
      if ((e.key === 'n' || e.key === 'N') && !dom.expenseModal.classList.contains('open') && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
        e.preventDefault();
        openModal(false);
      }
    });

    // Category Preset Chips
    dom.categoryChips.querySelectorAll('.chip').forEach(chip => {
      chip.addEventListener('click', () => {
        dom.formCategory.value = chip.dataset.cat;
        updateChipSelection(chip.dataset.cat);
      });
    });

    dom.formCategory.addEventListener('input', (e) => {
      updateChipSelection(e.target.value);
    });

    // Realtime Search
    dom.searchInput.addEventListener('input', (e) => {
      state.searchQuery = e.target.value;
      dom.clearSearchBtn.style.display = state.searchQuery ? 'block' : 'none';
      renderExpensesTable();
    });

    dom.clearSearchBtn.addEventListener('click', () => {
      dom.searchInput.value = '';
      state.searchQuery = '';
      dom.clearSearchBtn.style.display = 'none';
      renderExpensesTable();
      dom.searchInput.focus();
    });

    // Filters
    dom.categoryFilter.addEventListener('change', (e) => {
      state.selectedCategoryFilter = e.target.value;
      loadExpenses();
    });

    dom.startDateFilter.addEventListener('change', (e) => {
      state.startDateFilter = e.target.value;
      loadExpenses();
    });

    dom.endDateFilter.addEventListener('change', (e) => {
      state.endDateFilter = e.target.value;
      loadExpenses();
    });

    dom.resetFiltersBtn.addEventListener('click', () => {
      dom.searchInput.value = '';
      dom.categoryFilter.value = '';
      dom.startDateFilter.value = '';
      dom.endDateFilter.value = '';
      state.searchQuery = '';
      state.selectedCategoryFilter = '';
      state.startDateFilter = '';
      state.endDateFilter = '';
      dom.clearSearchBtn.style.display = 'none';
      loadExpenses();
    });

    // Monthly Picker
    dom.monthlyYearSelect.addEventListener('change', (e) => {
      state.selectedYear = parseInt(e.target.value, 10);
      loadMonthlySummary();
    });

    dom.monthlyMonthSelect.addEventListener('change', (e) => {
      state.selectedMonth = parseInt(e.target.value, 10);
      loadMonthlySummary();
    });
  }

  // ---------------------------------------------------------------------------
  // Application Bootstrap
  // ---------------------------------------------------------------------------
  function init() {
    applyTheme(state.theme);
    dom.currencySelect.value = state.currency;
    dom.formCurrencyPrefix.textContent = state.currency;
    populateYearSelector();
    setupEventListeners();
    loadAllData();
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

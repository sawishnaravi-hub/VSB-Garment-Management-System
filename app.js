// =========================================================
// VSB GARMENT MANUFACTURING - INTERACTIVE FRONTEND JS
// =========================================================

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('show');
        });
    }

    // 2. Initialize Dashboard Charts if on Dashboard page
    const incomeExpenseCanvas = document.getElementById('chartIncomeExpense');
    if (incomeExpenseCanvas) {
        initDashboardCharts();
    }

    // 3. Dynamic Calculation: Sales Modal (Quantity * Selling Price = Total)
    const saleQty = document.getElementById('saleQuantity');
    const salePrice = document.getElementById('salePrice');
    const saleTotal = document.getElementById('saleTotal');
    const saleProductSelect = document.getElementById('saleProductSelect');

    if (saleQty && salePrice && saleTotal) {
        const updateSaleTotal = () => {
            const q = parseFloat(saleQty.value) || 0;
            const p = parseFloat(salePrice.value) || 0;
            saleTotal.value = (q * p).toFixed(2);
        };
        saleQty.addEventListener('input', updateSaleTotal);
        salePrice.addEventListener('input', updateSaleTotal);

        if (saleProductSelect) {
            saleProductSelect.addEventListener('change', (e) => {
                const opt = e.target.options[e.target.selectedIndex];
                const price = opt.getAttribute('data-price');
                const stock = opt.getAttribute('data-stock');
                if (price) {
                    salePrice.value = parseFloat(price).toFixed(2);
                }
                const stockNotice = document.getElementById('saleStockNotice');
                if (stockNotice && stock !== null) {
                    stockNotice.textContent = `Available Stock: ${stock} units`;
                    if (parseInt(stock) <= 0) {
                        stockNotice.className = 'form-text text-danger fw-bold';
                    } else {
                        stockNotice.className = 'form-text text-success';
                    }
                }
                updateSaleTotal();
            });
        }
    }

    // 4. Dynamic Calculation: Raw Material Modal (Quantity * Cost Per Unit = Total Cost)
    const matQty = document.getElementById('matQuantity');
    const matUnitCost = document.getElementById('matUnitCost');
    const matTotal = document.getElementById('matTotalCost');
    if (matQty && matUnitCost && matTotal) {
        const updateMatTotal = () => {
            const q = parseFloat(matQty.value) || 0;
            const c = parseFloat(matUnitCost.value) || 0;
            matTotal.value = (q * c).toFixed(2);
        };
        matQty.addEventListener('input', updateMatTotal);
        matUnitCost.addEventListener('input', updateMatTotal);
    }

    // 5. Dynamic Calculation: Salary Modal (Basic + Bonus - Deduction = Net)
    const salWorkerSelect = document.getElementById('salWorkerSelect');
    const salBasic = document.getElementById('salBasic');
    const salBonus = document.getElementById('salBonus');
    const salDeduction = document.getElementById('salDeduction');
    const salNet = document.getElementById('salNet');

    if (salBasic && salBonus && salDeduction && salNet) {
        const updateNetSalary = () => {
            const b = parseFloat(salBasic.value) || 0;
            const bo = parseFloat(salBonus.value) || 0;
            const d = parseFloat(salDeduction.value) || 0;
            const net = Math.max(0, b + bo - d);
            salNet.value = net.toFixed(2);
        };
        salBonus.addEventListener('input', updateNetSalary);
        salDeduction.addEventListener('input', updateNetSalary);

        if (salWorkerSelect) {
            salWorkerSelect.addEventListener('change', (e) => {
                const opt = e.target.options[e.target.selectedIndex];
                const baseSal = opt.getAttribute('data-salary');
                if (baseSal) {
                    salBasic.value = parseFloat(baseSal).toFixed(2);
                }
                updateNetSalary();
            });
        }
    }

    // 6. Quick Client-Side Table Filter
    const liveFilterInput = document.getElementById('tableLiveFilter');
    if (liveFilterInput) {
        liveFilterInput.addEventListener('keyup', () => {
            const term = liveFilterInput.value.toLowerCase();
            const rows = document.querySelectorAll('.data-table tbody tr');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(term) ? '' : 'none';
            });
        });
    }
});

// Chart.js initialization function
async function initDashboardCharts() {
    try {
        const response = await fetch('/api/dashboard-charts');
        if (!response.ok) return;
        const data = await response.json();

        // 1. Chart 1: Monthly Income vs Expenses (Bar)
        const ctxIncExp = document.getElementById('chartIncomeExpense');
        if (ctxIncExp) {
            new Chart(ctxIncExp, {
                type: 'bar',
                data: {
                    labels: data.monthly_labels,
                    datasets: [
                        {
                            label: 'Total Income (₹)',
                            data: data.monthly_income,
                            backgroundColor: 'rgba(16, 185, 129, 0.85)',
                            borderColor: '#10b981',
                            borderWidth: 1,
                            borderRadius: 6
                        },
                        {
                            label: 'Total Expenses (₹)',
                            data: data.monthly_expenses,
                            backgroundColor: 'rgba(239, 68, 68, 0.85)',
                            borderColor: '#ef4444',
                            borderWidth: 1,
                            borderRadius: 6
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top' },
                        tooltip: {
                            callbacks: {
                                label: ctx => `${ctx.dataset.label}: ₹${Number(ctx.raw).toLocaleString('en-IN')}`
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { callback: v => '₹' + v.toLocaleString('en-IN') }
                        }
                    }
                }
            });
        }

        // 2. Chart 2: Monthly Profit Trend (Line)
        const ctxProfit = document.getElementById('chartProfit');
        if (ctxProfit) {
            new Chart(ctxProfit, {
                type: 'line',
                data: {
                    labels: data.monthly_labels,
                    datasets: [{
                        label: 'Net Profit (₹)',
                        data: data.monthly_profit,
                        borderColor: '#0284c7',
                        backgroundColor: 'rgba(2, 132, 199, 0.12)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.35,
                        pointBackgroundColor: '#0284c7',
                        pointRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top' },
                        tooltip: {
                            callbacks: {
                                label: ctx => `Profit: ₹${Number(ctx.raw).toLocaleString('en-IN')}`
                            }
                        }
                    },
                    scales: {
                        y: {
                            ticks: { callback: v => '₹' + v.toLocaleString('en-IN') }
                        }
                    }
                }
            });
        }

        // 3. Chart 3: Product Sales Distribution (Doughnut)
        const ctxSales = document.getElementById('chartProductSales');
        if (ctxSales && data.product_sales_labels.length > 0) {
            new Chart(ctxSales, {
                type: 'doughnut',
                data: {
                    labels: data.product_sales_labels,
                    datasets: [{
                        data: data.product_sales_data,
                        backgroundColor: [
                            '#0284c7', '#0d9488', '#8b5cf6', '#f59e0b',
                            '#ec4899', '#3b82f6', '#10b981', '#6366f1'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'right' }
                    }
                }
            });
        }

        // 4. Chart 4: Expense Categories (Pie)
        const ctxExp = document.getElementById('chartExpenseCategory');
        if (ctxExp && data.expense_cat_labels.length > 0) {
            new Chart(ctxExp, {
                type: 'pie',
                data: {
                    labels: data.expense_cat_labels,
                    datasets: [{
                        data: data.expense_cat_data,
                        backgroundColor: [
                            '#ef4444', '#f59e0b', '#10b981', '#06b6d4',
                            '#8b5cf6', '#ec4899', '#64748b', '#0284c7', '#14b8a6'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'right' },
                        tooltip: {
                            callbacks: {
                                label: ctx => `${ctx.label}: ₹${Number(ctx.raw).toLocaleString('en-IN')}`
                            }
                        }
                    }
                }
            });
        }

        // 5. Chart 5: Production Quantity (Bar)
        const ctxProd = document.getElementById('chartProduction');
        if (ctxProd && data.production_labels.length > 0) {
            new Chart(ctxProd, {
                type: 'bar',
                data: {
                    labels: data.production_labels,
                    datasets: [{
                        label: 'Units Produced',
                        data: data.production_data,
                        backgroundColor: 'rgba(13, 148, 136, 0.85)',
                        borderColor: '#0d9488',
                        borderWidth: 1,
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top' }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { precision: 0 }
                        }
                    }
                }
            });
        }

    } catch (err) {
        console.error('Error loading dashboard charts:', err);
    }
}

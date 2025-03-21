   // Дані для заповнення таблиць
   const dataX = [
    [2.7, 26, 19, 0.11],
    [1.5, 25, 11, 0.12],
    [2.5, 42, 14, 0.21],
    [4, 29, 17, 0.16],
    [1.2, 40, 17, 0.4],
    [1.7, 42, 20, 0.3],
    [2.5, 44, 17, 0.25]
];

const dataY = [
    [3.5, 35, 19, 0.21],
    [4.1, 60, 14, 0.08],
    [2.8, 58, 10, 0.22],
    [2.5, 65, 18, 0.13],
    [2.6, 74, 19, 0.33],
    [5.0, 27, 11, 0.83],
    [3.5, 31, 15, 0.5]
];

const dataZ1 = [3.6, 62, 13, 0.45];
const dataZ2 = [2.6, 49, 16, 0.41];

// Функція для заповнення таблиць
function fillTables() {
        fillTable('dataTableXij', dataX);
        fillTable('dataTableYij', dataY);
        fillTable('dataTableZone', [dataZ1]);
        fillTable('dataTableZtwo', [dataZ2]);
    }

    // Функція для заповнення конкретної таблиці
    function fillTable(tableId, data) {
        const table = document.getElementById(tableId);
        const rows = table.querySelectorAll('tr');
        for (let i = 0; i < rows.length - 1; i++) {
            const inputs = rows[i + 1].querySelectorAll('input');
            for (let j = 0; j < inputs.length; j++) {
                inputs[j].value = data[i][j];
            }
        }
    }

    // Інші функції залишаються незмінними
    function getDataFromTable(tableId) {
        const table = document.getElementById(tableId);
        const rows = table.querySelectorAll('tr');
        const data = [];
        for (let i = 1; i < rows.length; i++) {
            const inputs = rows[i].querySelectorAll('input');
            const rowData = Array.from(inputs).map(input => parseFloat(input.value));
            if (rowData.some(isNaN)) {
                throw new Error(`Некоректні дані у таблиці ${tableId}.`);
            }
            data.push(rowData);
        }
        return data;
    }

    function calculateMean(data) {
        const n = data.length;
        const p = data[0].length;
        const mean = new Array(p).fill(0);
        for (let i = 0; i < n; i++) {
            for (let j = 0; j < p; j++) {
                mean[j] += data[i][j];
            }
        }
        return mean.map(val => val / n);
    }

    function calculateCovarianceMatrix(data, mean) {
        const n = data.length;
        const p = data[0].length;
        const cov = new Array(p).fill(0).map(() => new Array(p).fill(0));
        for (let i = 0; i < n; i++) {
            for (let j = 0; j < p; j++) {
                for (let k = 0; k < p; k++) {
                    cov[j][k] += (data[i][j] - mean[j]) * (data[i][k] - mean[k]);
                }
            }
        }
        return multiplyMatrixByScalar(cov, 1 / n);
    }

    function multiplyMatrixByScalar(matrix, scalar) {
        return matrix.map(row => row.map(val => val * scalar));
    }

    function addMatrices(matrix1, matrix2) {
        return matrix1.map((row, i) => row.map((val, j) => val + matrix2[i][j]));
    }

    function subtractVectors(vec1, vec2) {
        return vec1.map((val, i) => val - vec2[i]);
    }

    function matrixMultiply(matrix, vector) {
        return matrix.map(row => dotProduct(row, vector));
    }

    function dotProduct(vec1, vec2) {
        if (vec1.length !== vec2.length) {
            throw new Error("Вектори мають різну довжину.");
        }
        return vec1.reduce((sum, val, i) => sum + val * vec2[i], 0);
    }

    function inverseMatrix(matrix) {
        if (matrix.length !== matrix[0].length) {
            throw new Error("Матриця не є квадратною.");
        }
        const n = matrix.length;
        const identity = Array.from({ length: n }, (_, i) =>
            Array.from({ length: n }, (_, j) => (i === j ? 1 : 0))
        );
        const augmented = matrix.map((row, i) => [...row, ...identity[i]]);

        for (let i = 0; i < n; i++) {
            if (augmented[i][i] === 0) {
                let swapRow = -1;
                for (let j = i + 1; j < n; j++) {
                    if (augmented[j][i] !== 0) {
                        swapRow = j;
                        break;
                    }
                }
                if (swapRow === -1) {
                    throw new Error("Матриця не має оберненої (визначник дорівнює нулю).");
                }
                [augmented[i], augmented[swapRow]] = [augmented[swapRow], augmented[i]];
            }
            const pivot = augmented[i][i];
            for (let j = 0; j < 2 * n; j++) {
                augmented[i][j] /= pivot;
            }
            for (let j = 0; j < n; j++) {
                if (j !== i) {
                    const factor = augmented[j][i];
                    for (let k = 0; k < 2 * n; k++) {
                        augmented[j][k] -= factor * augmented[i][k];
                    }
                }
            }
        }
        return augmented.map(row => row.slice(n));
    }

    function calculateClusters() {
    try {
        const steps = []; // Масив для зберігання кроків
        const addStep = (title, content) => {
            steps.push({ title, content });
        };

        // Отримання даних з таблиць
        const X = getDataFromTable('dataTableXij');
        const Y = getDataFromTable('dataTableYij');
        const Z1 = getDataFromTable('dataTableZone')[0];
        const Z2 = getDataFromTable('dataTableZtwo')[0];

        addStep("Вхідні дані X", X);
        addStep("Вхідні дані Y", Y);
        addStep("Вхідні дані Z1", Z1);
        addStep("Вхідні дані Z2", Z2);

        // Перевірка на коректність вхідних даних
        if (!X.length || !Y.length || !Z1.length || !Z2.length) {
            throw new Error("Будь ласка, заповніть всі поля таблиць.");
        }

        // Обчислення середніх значень
        const meanX = calculateMean(X);
        const meanY = calculateMean(Y);

        addStep("Середнє значення X", meanX);
        addStep("Середнє значення Y", meanY);

        // Обчислення коваріаційних матриць
        const covX = calculateCovarianceMatrix(X, meanX);
        const covY = calculateCovarianceMatrix(Y, meanY);

        addStep("Коваріаційна матриця X", covX);
        addStep("Коваріаційна матриця Y", covY);

        // Обчислення об'єднаної коваріаційної матриці
        const n1 = X.length;
        const n2 = Y.length;
        const S = multiplyMatrixByScalar(
            addMatrices(multiplyMatrixByScalar(covX, n1), multiplyMatrixByScalar(covY, n2)),
            1 / (n1 + n2 - 2)
        );

        addStep("Об'єднана коваріаційна матриця S", S);

        // Обчислення оберненої матриці S
        const S_inv = inverseMatrix(S);

        addStep("Обернена матриця S<sup>-1</sup>", S_inv);

        // Обчислення вектора A
        const A = matrixMultiply(S_inv, subtractVectors(meanX, meanY));

        addStep("Вектор A", A);

        // Обчислення проекцій Ux та Uy
        const Ux = X.map(row => dotProduct(row, A));
        const Uy = Y.map(row => dotProduct(row, A));

        addStep("Проекції Ux", Ux);
        addStep("Проекції Uy", Uy);

        // Обчислення середніх значень Ux та Uy
        const meanUx = Ux.reduce((sum, val) => sum + val, 0) / n1;
        const meanUy = Uy.reduce((sum, val) => sum + val, 0) / n2;

        addStep("Середнє значення Ux", meanUx);
        addStep("Середнє значення Uy", meanUy);

        // Обчислення порогового значення C
        const C = (meanUx + meanUy) / 2;

        addStep("Порогове значення C", C);

        // Обчислення проекцій Uz1 та Uz2
        const Uz1 = dotProduct(Z1, A);
        const Uz2 = dotProduct(Z2, A);

        addStep("Проекція Uz1", Uz1);
        addStep("Проекція Uz2", Uz2);

        // Визначення класу для Z1 та Z2
        const resultZ1 = Uz1 >= C ? 'X' : 'Y';
        const resultZ2 = Uz2 >= C ? 'X' : 'Y';

        addStep("Результат для Z1", `Z1 належить до класу: ${resultZ1}`);
        addStep("Результат для Z2", `Z2 належить до класу: ${resultZ2}`);

        // Виведення результатів
        document.getElementById('result').innerHTML = `
        <div class="results-container">
            <h2 class="results-title">Результати:</h2>
            <p class="result-text">
                Z1 належить до класу: <strong>${resultZ1}</strong><br>
                Z2 належить до класу: <strong>${resultZ2}</strong>
            </p>
        </div>
        `;

        // Виведення кроків
        const stepsContainer = document.getElementById('steps');
        stepsContainer.innerHTML = steps.map((step, index) => {
            let contentHtml;

            if (Array.isArray(step.content)) {
                // Якщо content — це масив (матриця або вектор)
                if (step.content.every(row => Array.isArray(row))) {
                    // Якщо це двовимірний масив (матриця)
                    contentHtml = `
                        <table>
                            ${step.content.map(row => `
                                <tr>
                                    ${row.map(cell => `<td>${cell}</td>`).join('')}
                                </tr>
                            `).join('')}
                        </table>
                    `;
                } else {
                    // Якщо це одновимірний масив (вектор)
                    contentHtml = `
                        <table>
                            <tr>
                                ${step.content.map(cell => `<td>${cell}</td>`).join('')}
                            </tr>
                        </table>
                    `;
                }
            } else if (typeof step.content === 'object' && step.content !== null) {
                // Якщо content — це об'єкт (наприклад, JSON)
                contentHtml = `<pre>${JSON.stringify(step.content, null, 2)}</pre>`;
            } else {
                // Якщо content — це простий текст або число
                contentHtml = `<p>${step.content}</p>`;
            }

            return `
                <div class="step">
                    <h3>Крок ${index + 1}: ${step.title}</h3>
                    ${contentHtml}
                </div>
            `;
        }).join('');
    } 
    catch (error) {
        document.getElementById('result').innerHTML = `<span class="error">Помилка: ${error.message}</span>`;
    }
}
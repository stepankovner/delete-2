import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt

# --- ЛОГИКА РАСЧЕТА ---
def simulate_flyby(m_meteor, x_init, y_init, vx_init, vy_init, dt, total_steps):
    # Физические константы
    G = 6.67430e-11
    M_earth = 5.972e24
    R_earth = 6371000  # Радиус Земли в метрах
    
    x, y = x_init, y_init
    vx, vy = vx_init, vy_init
    
    trajectory = []
    min_distance = float('inf')
    max_force = 0
    collision = False

    for step in range(total_steps):
        r = math.sqrt(x**2 + y**2)
        
        # Проверка на столкновение с Землей
        if r <= R_earth:
            collision = True
            break
            
        force = G * (M_earth * m_meteor) / (r**2)
        
        if force > max_force: max_force = force
        if r < min_distance: min_distance = r
            
        a = force / m_meteor
        ax = -a * (x / r)
        ay = -a * (y / r)
        
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
        
        # Сохраняем каждую 5-ю точку для плавности графика без тормозов
        if step % 5 == 0:
            trajectory.append({
                "x": x, 
                "y": y, 
                "v_km_s": math.sqrt(vx**2 + vy**2) / 1000,
                "r_km": r / 1000
            })
            
    return pd.DataFrame(trajectory), min_distance, max_force, collision

# --- ИНТЕРФЕЙС STREAMLIT ---
st.set_page_config(page_title="Meteor Sim 2.0", layout="wide")

st.title("☄️ Симуляция гравитационного маневра")
st.write("Senior-level визуализация пролета тела вблизи Земли.")

# Сайдбар с настройками
st.sidebar.header("🚀 Параметры миссии")
m_meteor = st.sidebar.number_input("Масса объекта (кг)", value=50000, step=1000)
dt = st.sidebar.slider("Точность (шаг dt, сек)", 1, 300, 60)
steps = st.sidebar.number_input("Длительность (кол-во шагов)", value=2000, step=100)

st.sidebar.header("📍 Начальные условия")
x_start = st.sidebar.number_input("Начальная позиция X (м)", value=-40000000)
y_start = st.sidebar.number_input("Начальная позиция Y (м)", value=12000000)
vx_start = st.sidebar.number_input("Начальная скорость Vx (м/с)", value=10000)
vy_start = st.sidebar.number_input("Начальная скорость Vy (м/с)", value=500)

# Запуск расчета
df, min_dist, max_f, is_dead = simulate_flyby(m_meteor, x_start, y_start, vx_start, vy_start, dt, steps)

# Верхние метрики
c1, c2, c3 = st.columns(3)
c1.metric("Перигей (мин. дист)", f"{min_dist/1000:.2f} км")
c2.metric("Пиковая сила", f"{max_f:.2e} Н")
c3.metric("Статус", "💥 СТОЛКНОВЕНИЕ" if is_dead else "✅ ПРОЛЕТ")

if is_dead:
    st.error("Объект вошел в атмосферу или врезался в поверхность!")

# --- ГРАФИК MATPLOTLIB ---
st.subheader("Визуализация траектории")

fig, ax = plt.subplots(figsize=(10, 7))

earth_radius = 6371000
earth_circle = plt.Circle((0, 0), earth_radius, color='#1E90FF', label='Земля', alpha=0.7)
ax.add_patch(earth_circle)

# Рисуем атмосферу (декоративно)
atmo_circle = plt.Circle((0, 0), earth_radius + 500000, color='#87CEEB', alpha=0.2, label='Атмосфера')
ax.add_patch(atmo_circle)

# Траектория
ax.plot(df['x'], df['y'], color='#FF4500', label='Путь метеорита', linewidth=2)
ax.scatter(df['x'].iloc[0], df['y'].iloc[0], color='green', s=100, label='Старт', zorder=5)

# Настройка осей (Equal обязателен, чтобы Земля не была яйцом)
ax.set_aspect('equal', adjustable='datalim')
ax.grid(True, which='both', linestyle='--', alpha=0.3)
ax.axhline(0, color='white', linewidth=0.5)
ax.axvline(0, color='white', linewidth=0.5)

# Стиль
plt.style.use('dark_background')
fig.patch.set_facecolor('#0E1117')
ax.set_facecolor('#0E1117')
ax.set_xlabel("X (метры)", fontsize=10)
ax.set_ylabel("Y (метры)", fontsize=10)
ax.legend()

st.pyplot(fig)

# График скорости (дополнительный понт для препода)
st.subheader("Динамика скорости (км/с)")
st.line_chart(df.set_index('r_km')['v_km_s'])
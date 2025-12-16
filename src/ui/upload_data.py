import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def render_upload_data():

    # Verificar se já temos dados em cache
    if 'uploaded_data' in st.session_state and st.session_state.uploaded_data is not None:
        st.success("✅ Dataset loaded!")
        df = st.session_state.uploaded_data

        # Visualizações do dataset
        _render_dataset_analytics(df)

        with st.expander("👁️ Data preview (cached)"):
            st.dataframe(df.head())
            st.caption(f"Total of {len(df)} companies inside the dataset")

        # Opção para recarregar
        if st.button("🔄 Load new Dataset"):
            st.session_state.uploaded_data = None
            st.rerun()

        return df
    
    uploaded_file = st.file_uploader(
        "Choose .CSV or .XLSX", 
        type=["csv", "xlsx"]
    )
    
    if uploaded_file is None:
        _render_sample_data()
        return None
    
    try:
        # Ler o arquivo
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Validar colunas necessárias
        colunas_necessarias = ['Nome', 'Website', 'Descrição Atividade']
        if all(col in df.columns for col in colunas_necessarias):
            st.success("✅ Dataset loaded with success!")

            # Salvar em cache (session state)
            st.session_state.uploaded_data = df
            st.session_state.dataset_source = uploaded_file.name

            # Visualizações do dataset
            _render_dataset_analytics(df)

            # Preview dos dados
            with st.expander("👁️ Data Preview"):
                st.dataframe(df.head())
                st.caption(f"Total of {len(df)} companies inside the dataset")

            return df
        else:
            st.error(
                f"❌ Necessary columns not found. "
                f"Necessary: {colunas_necessarias}"
            )
            return None
            
    except Exception as e:
        st.error(f"❌ Error loading dataset: {str(e)}")
        return None


def _render_dataset_analytics(df: pd.DataFrame):
    """
    Renderiza análises visuais do dataset carregado
    """
    st.markdown("---")
    st.subheader("📊 Análise do Dataset")

    # Análise de websites
    df_analysis = df.copy()

    # Verificar se website existe e não está vazio
    df_analysis['Has_Website'] = df_analysis['Website'].notna() & (df_analysis['Website'].str.strip() != '')

    # Contar empresas com e sem website
    has_website_count = df_analysis['Has_Website'].sum()
    no_website_count = len(df_analysis) - has_website_count
    total = len(df_analysis)

    # Percentagens
    has_website_pct = (has_website_count / total * 100) if total > 0 else 0
    no_website_pct = (no_website_count / total * 100) if total > 0 else 0

    # === MÉTRICAS PRINCIPAIS ===
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📈 Total de Empresas",
            value=f"{total:,}",
            delta=None
        )

    with col2:
        st.metric(
            label="✅ Com Website",
            value=f"{has_website_count:,}",
            delta=f"{has_website_pct:.1f}%"
        )

    with col3:
        st.metric(
            label="❌ Sem Website",
            value=f"{no_website_count:,}",
            delta=f"{no_website_pct:.1f}%",
            delta_color="inverse"
        )

    with col4:
        st.metric(
            label="📊 Completude",
            value=f"{has_website_pct:.1f}%",
            delta="Website data"
        )

    st.markdown("---")

    # === GRÁFICOS ===
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        # Gráfico de Donut - Websites
        fig_donut = go.Figure(data=[go.Pie(
            labels=['Com Website', 'Sem Website'],
            values=[has_website_count, no_website_count],
            hole=0.5,
            marker=dict(colors=['#00D26A', '#FF4B4B']),
            textinfo='label+percent',
            textposition='outside',
            hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<br>Percentagem: %{percent}<extra></extra>'
        )])

        fig_donut.update_layout(
            title={
                'text': '🌐 Distribuição de Websites',
                'x': 0.5,
                'xanchor': 'center'
            },
            showlegend=True,
            height=400,
            annotations=[dict(
                text=f'{has_website_pct:.1f}%',
                x=0.5, y=0.5,
                font_size=24,
                showarrow=False
            )]
        )

        st.plotly_chart(fig_donut, use_container_width=True)

    with col_chart2:
        # Gráfico de Barras - Comparação
        fig_bar = go.Figure(data=[
            go.Bar(
                x=['Com Website', 'Sem Website'],
                y=[has_website_count, no_website_count],
                text=[f'{has_website_count}<br>({has_website_pct:.1f}%)',
                      f'{no_website_count}<br>({no_website_pct:.1f}%)'],
                textposition='auto',
                marker=dict(color=['#00D26A', '#FF4B4B']),
                hovertemplate='<b>%{x}</b><br>Quantidade: %{y}<extra></extra>'
            )
        ])

        fig_bar.update_layout(
            title={
                'text': '📊 Comparação Quantitativa',
                'x': 0.5,
                'xanchor': 'center'
            },
            yaxis_title='Número de Empresas',
            showlegend=False,
            height=400
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    # === FILTRO POR REGIÃO (se existir) ===
    # Detectar coluna de região/localização
    region_columns = [col for col in df.columns if any(keyword in col.lower()
                      for keyword in ['concelho'])]

    if region_columns:
        st.markdown("---")
        st.subheader("🗺️ Análise por Região")

        # Usar a primeira coluna de região encontrada
        region_col = region_columns[0]

        # Filtro de região
        col_filter, col_empty = st.columns([1, 2])
        with col_filter:
            regions = ['Todas'] + sorted(df_analysis[region_col].dropna().unique().tolist())
            selected_region = st.selectbox(
                f"Filtrar por {region_col}:",
                regions,
                key="region_filter"
            )

        # Filtrar dados
        if selected_region != 'Todas':
            df_filtered = df_analysis[df_analysis[region_col] == selected_region]
        else:
            df_filtered = df_analysis

        # Análise por região
        region_analysis = df_filtered.groupby(region_col).agg({
            'Has_Website': ['count', 'sum']
        }).reset_index()

        region_analysis.columns = [region_col, 'Total', 'Com_Website']
        region_analysis['Sem_Website'] = region_analysis['Total'] - region_analysis['Com_Website']
        region_analysis['Percentagem_Com_Website'] = (region_analysis['Com_Website'] / region_analysis['Total'] * 100).round(1)

        # Ordenar por total
        region_analysis = region_analysis.sort_values('Total', ascending=False)

        # Gráfico de barras empilhadas por região
        fig_region = go.Figure()

        fig_region.add_trace(go.Bar(
            name='Com Website',
            x=region_analysis[region_col],
            y=region_analysis['Com_Website'],
            marker_color='#00D26A',
            hovertemplate='<b>%{x}</b><br>Com Website: %{y}<extra></extra>'
        ))

        fig_region.add_trace(go.Bar(
            name='Sem Website',
            x=region_analysis[region_col],
            y=region_analysis['Sem_Website'],
            marker_color='#FF4B4B',
            hovertemplate='<b>%{x}</b><br>Sem Website: %{y}<extra></extra>'
        ))

        fig_region.update_layout(
            title=f'📍 Distribuição por {region_col}',
            barmode='stack',
            xaxis_title=region_col,
            yaxis_title='Número de Empresas',
            height=400,
            showlegend=True
        )

        st.plotly_chart(fig_region, use_container_width=True)

        # Tabela detalhada
        with st.expander("📋 Tabela Detalhada por Região"):
            # Formatar tabela para display
            display_df = region_analysis.copy()
            display_df['Percentagem_Com_Website'] = display_df['Percentagem_Com_Website'].apply(lambda x: f"{x}%")

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    region_col: st.column_config.TextColumn(region_col, width="medium"),
                    "Total": st.column_config.NumberColumn("Total", format="%d"),
                    "Com_Website": st.column_config.NumberColumn("Com Website", format="%d"),
                    "Sem_Website": st.column_config.NumberColumn("Sem Website", format="%d"),
                    "Percentagem_Com_Website": st.column_config.TextColumn("% Com Website"),
                }
            )

    # === INSIGHTS ===
    st.markdown("---")
    st.subheader("💡 Insights")

    col_insight1, col_insight2 = st.columns(2)

    with col_insight1:
        if has_website_pct >= 80:
            st.success("✅ **Excelente**: Mais de 80% das empresas têm website registado")
        elif has_website_pct >= 50:
            st.info("📊 **Bom**: Maioria das empresas tem website, mas há espaço para melhoria")
        else:
            st.warning("⚠️ **Atenção**: Menos de 50% das empresas têm website registado")

    with col_insight2:
        st.metric(
            label="🎯 Empresas Prontas para Análise",
            value=f"{has_website_count:,}",
            help="Empresas com website disponível para análise de segurança e lead scoring"
        )


def _render_sample_data():
    """
    Renderiza informações sobre dados de exemplo
    """
    st.info("👆 Upload a dataset or watch an example below:")
    
    # Dataset de exemplo
    sample_data = {
        'Nome': ['Tech Solutions', 'MediCare', 'EcoRetail'],
        'Website': [
            'https://techsolutions.com', 
            'https://medicare.com', 
            'https://ecoretail.com'
        ],
        'Descrição Atividade': [
            'Empresa especializada em desenvolvimento de software para startups.',
            'Fornecedor de equipamentos médicos e telemedicina.',
            'Plataforma de e-commerce sustentável com produtos ecológicos.'
        ]
    }
    
    sample_df = pd.DataFrame(sample_data)
    st.dataframe(sample_df)
    
    # Informações sobre o formato
    st.markdown("### 📝 Necessary Format")
    st.markdown("""
    The dataset must contain the following columns:
    - **Nome**: Nome da empresa
    - **Website**: URL do website  
    - **Descrição Atividade**: Descrição detalhada da empresa
    
    **Accepted formats:** CSV, Excel (.xlsx)
    """)

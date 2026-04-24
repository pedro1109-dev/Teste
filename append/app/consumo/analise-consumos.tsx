import React, { useState } from 'react';
import MenuLateral from '../../components/Menulateral';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Feather, Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { theme } from '../../constants/theme';

const BAR_MAX_HEIGHT = 140;

type Periodo = '1mes' | '3meses' | '6meses' | '1ano';

const dadosPorPeriodo: Record<Periodo, { label: string; valor: number }[]> = {
  '1mes': [
    { label: 'Sem 1', valor: 220 },
    { label: 'Sem 2', valor: 235 },
    { label: 'Sem 3', valor: 210 },
    { label: 'Sem 4', valor: 250 },
  ],
  '3meses': [
    { label: 'Jan', valor: 680 },
    { label: 'Fev', valor: 720 },
    { label: 'Mar', valor: 915 },
  ],
  '6meses': [
    { label: 'Out', valor: 540 },
    { label: 'Nov', valor: 610 },
    { label: 'Dez', valor: 750 },
    { label: 'Jan', valor: 680 },
    { label: 'Fev', valor: 720 },
    { label: 'Mar', valor: 915 },
  ],
  '1ano': [
    { label: 'Abr', valor: 480 },
    { label: 'Mai', valor: 510 },
    { label: 'Jun', valor: 490 },
    { label: 'Jul', valor: 560 },
    { label: 'Ago', valor: 530 },
    { label: 'Set', valor: 580 },
    { label: 'Out', valor: 540 },
    { label: 'Nov', valor: 610 },
    { label: 'Dez', valor: 750 },
    { label: 'Jan', valor: 680 },
    { label: 'Fev', valor: 720 },
    { label: 'Mar', valor: 915 },
  ],
};

const periodoLabels: Record<Periodo, string> = {
  '1mes': '1 mês',
  '3meses': '3 meses',
  '6meses': '6 meses',
  '1ano': '1 ano',
};

export default function AnaliseConsumos() {
  const router = useRouter();
  const [menuAberto, setMenuAberto] = useState(false);
  const [periodoAtivo, setPeriodoAtivo] = useState<Periodo>('1mes');

  const dados = dadosPorPeriodo[periodoAtivo];
  const maxValor = Math.max(...dados.map((d) => d.valor));
  const totalConsumos = 915.0;
  const totalRegistros = 4;
  const mediaGasto = totalConsumos / totalRegistros;

  return (
    <SafeAreaView style={styles.safe}>
      <LinearGradient
        colors={[
          theme.colors.backgroundTop,
          theme.colors.backgroundMid,
          theme.colors.backgroundBottom,
        ]}
        style={styles.container}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* HEADER */}
          <View style={styles.header}>
            <View style={styles.headerLeft}>
              <View style={styles.logoCircle}>
                <MaterialCommunityIcons name="leaf" size={22} color="#6EE86A" />
              </View>

              <View>
                <Text style={styles.headerBrand}>ECO CONTROL</Text>
                <Text style={styles.headerSub}>Análise de consumos</Text>
              </View>
            </View>

            <TouchableOpacity
              style={styles.circleButton}
              onPress={() => setMenuAberto(true)}
            >
              <Feather name="menu" size={24} color="#FFFFFF" />
            </TouchableOpacity>
          </View>

            {/* MAIN CARD */}
          <View style={styles.mainCard}>
            {/* Card Title */}
            <View style={styles.cardTitleRow}>
              <Text style={styles.cardTitle}>Análise de seus consumos</Text>
            </View>

            {/* STATS ROW */}
            <View style={styles.statsRow}>
              {/* Total */}
              <View style={styles.statBox}>
                <Text style={styles.statLabel}>Total de{'\n'}consumos</Text>
                <View style={styles.statIconWrap}>
                  <Ionicons name="cash-outline" size={20} color="#F5B731" />
                </View>
                <Text style={styles.statValueYellow}>
                  R${totalConsumos.toFixed(2).replace('.', ',')}
                </Text>
              </View>

              {/* Registros */}
              <View style={[styles.statBox, styles.statBoxCenter]}>
                <Text style={[styles.statLabel, styles.statLabelBlue]}>
                  Registros
                </Text>
                <View style={[styles.statIconWrap, styles.statIconBlue]}>
                  <Ionicons name="document-text-outline" size={20} color="#5BC4F5" />
                </View>
                <Text style={styles.statValueBlue}>{totalRegistros}</Text>
              </View>

              {/* Média */}
              <View style={styles.statBox}>
                <Text style={styles.statLabel}>Média de{'\n'}gasto</Text>
                <View style={styles.statIconWrap}>
                  <Ionicons name="calculator-outline" size={20} color="#F5B731" />
                </View>
                <Text style={styles.statValueYellow}>
                  R${mediaGasto.toFixed(2).replace('.', ',')}
                </Text>
              </View>
            </View>

            {/* DIVIDER */}
            <View style={styles.divider} />

            {/* CHART SECTION */}
            <View style={styles.chartSection}>
              <View style={styles.chartHeaderRow}>
                <View style={styles.chartTitleWrap}>
                  <Ionicons name="bar-chart" size={16} color="#6EE86A" />
                  <Text style={styles.chartTitle}>Consumo por período</Text>
                </View>
                <TouchableOpacity
                  style={styles.verRegistrosBtn}
                  onPress={() => router.push('/consumo/listagem-consumos' as any)}
                >
                  <Text style={styles.verRegistrosText}>Ver registros</Text>
                  <Ionicons name="chevron-forward" size={14} color="#6EE86A" />
                </TouchableOpacity>
              </View>

              {/* PERIODO TABS */}
              <ScrollView
                horizontal
                showsHorizontalScrollIndicator={false}
                style={styles.tabsScroll}
                contentContainerStyle={styles.tabsContent}
              >
                {(Object.keys(periodoLabels) as Periodo[]).map((p) => (
                  <TouchableOpacity
                    key={p}
                    style={[styles.tab, periodoAtivo === p && styles.tabActive]}
                    onPress={() => setPeriodoAtivo(p)}
                  >
                    <Text
                      style={[
                        styles.tabText,
                        periodoAtivo === p && styles.tabTextActive,
                      ]}
                    >
                      {periodoLabels[p]}
                    </Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>

              {/* BAR CHART */}
              <View style={styles.chartArea}>
                {/* Y-axis labels */}
                <View style={styles.yAxis}>
                  {[maxValor, Math.round(maxValor * 0.66), Math.round(maxValor * 0.33), 0].map(
                    (v, i) => (
                      <Text key={i} style={styles.yLabel}>
                        {v}
                      </Text>
                    )
                  )}
                </View>

                {/* Bars */}
                <ScrollView
                  horizontal
                  showsHorizontalScrollIndicator={false}
                  contentContainerStyle={styles.barsContainer}
                >
                  {dados.map((item, idx) => {
                    const barH = Math.max(
                      8,
                      (item.valor / maxValor) * BAR_MAX_HEIGHT
                    );
                    const isMax = item.valor === maxValor;
                    return (
                      <View key={idx} style={styles.barWrap}>
                        <Text style={styles.barValueLabel}>
                          {item.valor}
                        </Text>
                        <View style={styles.barTrack}>
                          <View
                            style={[
                              styles.bar,
                              { height: barH },
                              isMax && styles.barHighlight,
                            ]}
                          />
                        </View>
                        <Text style={styles.barXLabel}>{item.label}</Text>
                      </View>
                    );
                  })}
                </ScrollView>
              </View>

              {/* SUMMARY LINHA */}
              <View style={styles.summaryRow}>
                <View style={styles.summaryItem}>
                  <Text style={styles.summaryLabel}>Maior gasto</Text>
                  <Text style={styles.summaryValue}>
                    R${maxValor.toFixed(2).replace('.', ',')}
                  </Text>
                </View>
                <View style={styles.summaryDivider} />
                <View style={styles.summaryItem}>
                  <Text style={styles.summaryLabel}>Período</Text>
                  <Text style={styles.summaryValue}>
                    {periodoLabels[periodoAtivo]}
                  </Text>
                </View>
                <View style={styles.summaryDivider} />
                <View style={styles.summaryItem}>
                  <Text style={styles.summaryLabel}>Registros</Text>
                  <Text style={styles.summaryValue}>{dados.length}</Text>
                </View>
              </View>
            </View>
          </View>
        </ScrollView>

        {/* BOTTOM NAV */}
        <View style={styles.bottomNav}>
    <TouchableOpacity
      style={styles.navItem}
      onPress={() => router.push('/(tabs)/home')}
        >
          <Ionicons name="home-outline" size={20} color="#C7D6CE" />
          <Text style={styles.navText}>Início</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.navItemActive}>
          <Ionicons name="bar-chart" size={20} color="#7AF46C" />
          <Text style={styles.navTextActive}>Consumo</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navCenterButton}
          onPress={() => router.push('/consumo/registro-consumo')}
        >
          <Feather name="plus" size={26} color="#103221" />
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navItem}
          onPress={() => router.push('/metas' as any)}
        >
          <Feather name="target" size={20} color="#C7D6CE" />
          <Text style={styles.navText}>Metas</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navItem}
          onPress={() => router.push('/documento' as any)}
        >
          <MaterialCommunityIcons name="file-upload-outline" size={20} color="#C7D6CE" />
          <Text style={styles.navText}>Arquivo</Text>
        </TouchableOpacity>
    </View>
        <MenuLateral
      aberto={menuAberto}
      fechar={() => setMenuAberto(false)}
    />
      </LinearGradient>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: theme.colors.backgroundBottom,
  },
  container: {
    flex: 1,
  },
  circleButton: {
  width: 48,
  height: 48,
  borderRadius: 24,
  backgroundColor: 'rgba(255,255,255,0.05)',
  borderWidth: 1,
  borderColor: 'rgba(255,255,255,0.06)',
  alignItems: 'center',
  justifyContent: 'center',
},
  scrollContent: {
    paddingHorizontal: 16,
    paddingTop: 14,
    paddingBottom: 110,
  },

  // HEADER
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  logoCircle: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: 'rgba(120,255,140,0.08)',
    borderWidth: 1,
    borderColor: 'rgba(120,255,140,0.16)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10,
  },
  headerBrand: {
    color: '#E9F1EC',
    fontSize: 15,
    fontWeight: '800',
    letterSpacing: 0.6,
  },
  headerSub: {
    color: '#7AF46C',
    fontSize: 14,
    marginTop: 2,
  },
  menuButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
    alignItems: 'center',
    justifyContent: 'center',
  },

  // MAIN CARD
  mainCard: {
    backgroundColor: 'rgba(7, 47, 40, 0.94)',//cor de fundo
    borderRadius: 24,
    borderWidth: 1,
    borderColor: 'rgba(110,232,106,0.14)',
    overflow: 'hidden',
  },
  cardTitleRow: {
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 14,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(110,232,106,0.08)',
  },
  cardTitle: {
    color: '#F0FFF4',
    fontSize: 16,
    fontWeight: '800',
  },

  // STATS
  statsRow: {
    flexDirection: 'row',
    paddingHorizontal: 12,
    paddingVertical: 14,
    gap: 8,
  },
  statBox: {
    flex: 1,
    backgroundColor: 'rgba(18, 55, 40, 0.70)',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(110,232,106,0.10)',
    padding: 12,
    alignItems: 'flex-start',
    gap: 6,
  },
  statBoxCenter: {
    borderColor: 'rgba(91,196,245,0.20)',
    backgroundColor: 'rgba(15, 50, 70, 0.60)',
  },
  statLabel: {
    color: '#B8E8C4',
    fontSize: 12,
    fontWeight: '600',
    lineHeight: 16,
  },
  statLabelBlue: {
    color: '#90D4F5',
  },
  statIconWrap: {
    width: 34,
    height: 34,
    borderRadius: 10,
    backgroundColor: 'rgba(245,183,49,0.12)',
    borderWidth: 1,
    borderColor: 'rgba(245,183,49,0.18)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  statIconBlue: {
    backgroundColor: 'rgba(91,196,245,0.12)',
    borderColor: 'rgba(91,196,245,0.20)',
  },
  statValueYellow: {
    color: '#F5B731',
    fontSize: 14,
    fontWeight: '800',
  },
  statValueBlue: {
    color: '#5BC4F5',
    fontSize: 26,
    fontWeight: '800',
  },

  divider: {
    height: 1,
    backgroundColor: 'rgba(110,232,106,0.08)',
    marginHorizontal: 0,
  },

  // CHART SECTION
  chartSection: {
    padding: 14,
  },
  chartHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  chartTitleWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  chartTitle: {
    color: '#F0FFF4',
    fontSize: 14,
    fontWeight: '800',
  },
  verRegistrosBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(110,232,106,0.08)',
    borderWidth: 1,
    borderColor: 'rgba(110,232,106,0.18)',
    borderRadius: 20,
    paddingHorizontal: 10,
    paddingVertical: 5,
    gap: 2,
  },
  verRegistrosText: {
    color: '#6EE86A',
    fontSize: 12,
    fontWeight: '700',
  },

  // TABS
  tabsScroll: {
    marginBottom: 14,
  },
  tabsContent: {
    gap: 8,
    paddingRight: 4,
  },
  tab: {
    paddingHorizontal: 14,
    paddingVertical: 7,
    borderRadius: 20,
    backgroundColor: 'rgba(255,255,255,0.04)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.08)',
  },
  tabActive: {
    backgroundColor: '#6EE86A',
    borderColor: '#6EE86A',
  },
  tabText: {
    color: '#7AAF90',
    fontSize: 12,
    fontWeight: '600',
  },
  tabTextActive: {
    color: '#0D2B22',
    fontWeight: '800',
  },

  // CHART
  chartArea: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    marginBottom: 14,
    backgroundColor: 'rgba(5,30,22,0.5)',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(110,232,106,0.08)',
    padding: 12,
  },
  yAxis: {
    height: BAR_MAX_HEIGHT + 20,
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    marginRight: 8,
    paddingBottom: 18,
  },
  yLabel: {
    color: '#7AAF90',
    fontSize: 10,
    fontWeight: '500',
    width: 30,
    textAlign: 'right',
  },
  barsContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 10,
    paddingBottom: 0,
  },
  barWrap: {
    alignItems: 'center',
    gap: 4,
  },
  barValueLabel: {
    color: '#A8F5A0',
    fontSize: 10,
    fontWeight: '700',
  },
  barTrack: {
    width: 28,
    height: BAR_MAX_HEIGHT,
    justifyContent: 'flex-end',
  },
  bar: {
    width: 28,
    borderRadius: 8,
    backgroundColor: '#6EE86A',
    opacity: 0.82,
  },
  barHighlight: {
    opacity: 1,
    backgroundColor: '#A8F5A0',
  },
  barXLabel: {
    color: '#7AAF90',
    fontSize: 10,
    fontWeight: '500',
    marginTop: 2,
  },

  // SUMMARY
  summaryRow: {
    flexDirection: 'row',
    backgroundColor: 'rgba(18,55,40,0.55)',
    borderRadius: 14,
    borderWidth: 1,
    borderColor: 'rgba(110,232,106,0.10)',
    padding: 12,
  },
  summaryItem: {
    flex: 1,
    alignItems: 'center',
    gap: 4,
  },
  summaryDivider: {
    width: 1,
    backgroundColor: 'rgba(110,232,106,0.12)',
    marginVertical: 2,
  },
  summaryLabel: {
    color: '#7AAF90',
    fontSize: 11,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.3,
  },
  summaryValue: {
    color: '#F0FFF4',
    fontSize: 13,
    fontWeight: '800',
  },

  // BARRA DE TAREFAS
  bottomNav: {
    position: 'absolute',
    left: 18,
    right: 18,
    bottom: 14,
    height: 68,
    borderRadius: 24,
    backgroundColor: 'rgba(10, 38, 28, 0.98)',
    borderWidth: 1,
    borderColor: 'rgba(110,232,106,0.10)',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    paddingHorizontal: 10,
  },

  navItem: {
    width: 56,
    alignItems: 'center',
    justifyContent: 'center',
  },

  navItemActive: {
    width: 56,
    alignItems: 'center',
    justifyContent: 'center',
  },

  navCenterButton: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#6EE86A',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: -6,
    shadowColor: '#6EE86A',
    shadowOpacity: 0.30,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 4 },
    elevation: 8,
  },

  navText: {
    color: '#C7D6CE',
    fontSize: 10,
    marginTop: 2,
  },

  navTextActive: {
    color: '#7AF46C',
    fontSize: 10,
    fontWeight: '800',
    marginTop: 2,
  },
});
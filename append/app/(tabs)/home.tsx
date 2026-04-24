import React, { useState, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiFetch } from '../../services/api';
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
import { useRouter, useFocusEffect } from 'expo-router';
import { theme } from '../../constants/theme';

const coresGrafico = ['#6EEB62', '#7CE35A', '#FF6B4A', '#C6E34E', '#53D8FF'];

export default function Home() {
  const router = useRouter();

  const [usuario, setUsuario] = useState<any>(null);
  const [consumos, setConsumos] = useState<any[]>([]);
  const [tipoGrafico, setTipoGrafico] = useState<'tipo' | 'dia' | 'mes' | 'todos'>('tipo');
  const [menuAberto, setMenuAberto] = useState(false);
  const [carregando, setCarregando] = useState(true);

  const carregarHome = useCallback(async () => {
    try {
      setCarregando(true);

      const usuarioSalvo = await AsyncStorage.getItem('usuario');
      const usuarioId = await AsyncStorage.getItem('usuario_id');

      if (!usuarioSalvo || !usuarioId) {
        router.replace('/(auth)/login');
        return;
      }

      setUsuario(JSON.parse(usuarioSalvo));

      const dadosConsumo = await apiFetch(`/lista_consumo?id_usuario=${usuarioId}`);
      setConsumos(Array.isArray(dadosConsumo) ? dadosConsumo : []);
    } catch (error) {
      console.log('ERRO AO CARREGAR HOME:', error);
      setConsumos([]);
    } finally {
      setCarregando(false);
    }
  }, [router]);

  useFocusEffect(
    useCallback(() => {
      carregarHome();
    }, [carregarHome])
  );

  const resumoAgrupado = consumos.reduce((acc: any, item: any, index: number) => {
    const valorItem = Number(
      item.gasto ??
      item.valor ??
      item.valor_consumo ??
      item.valor_gasto ??
      item.valor_conta ??
      0
    );

    let chave =
      item.tipo ??
      item.tipo_consumo ??
      item.categoria ??
      item.tipo_recurso ??
      'Consumo';

    if (tipoGrafico === 'dia') {
      const dataItem = new Date(item.data ?? item.data_consumo ?? item.data_registro);
      chave = Number.isNaN(dataItem.getTime())
        ? 'Sem data'
        : `Dia ${String(dataItem.getDate()).padStart(2, '0')}`;
    }

    if (tipoGrafico === 'mes') {
      const dataItem = new Date(item.data ?? item.data_consumo ?? item.data_registro);
      chave = Number.isNaN(dataItem.getTime())
        ? 'Sem data'
        : `${String(dataItem.getMonth() + 1).padStart(2, '0')}/${dataItem.getFullYear()}`;
    }

    if (tipoGrafico === 'todos') {
      chave = `${chave} ${index + 1}`;
    }

    acc[chave] = (acc[chave] || 0) + valorItem;
    return acc;
  }, {});

  const chartData =
    consumos.length > 0
      ? Object.keys(resumoAgrupado)
          .sort((a, b) => resumoAgrupado[b] - resumoAgrupado[a])
          .slice(0, 7)
          .map((chave, index) => ({
            label: chave,
            value: resumoAgrupado[chave],
            color: coresGrafico[index % coresGrafico.length],
          }))
      : [{ label: 'Água', value: 0, color: '#6EEB62' }];

  const maxValue = Math.max(...chartData.map((item) => Number(item.value || 0)), 1);

  function formatarMoeda(valor: number) {
    return valor.toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    });
  }

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
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.header}>
            <View style={styles.headerLeft}>
              <View style={styles.avatar}>
                <MaterialCommunityIcons name="leaf" size={24} color="#8CFF8A" />
              </View>

              <View>
                <Text style={styles.title}>
                  {carregando
                    ? 'Carregando...'
                    : usuario?.nome
                    ? `Bem-vindo, ${usuario.nome}!`
                    : 'Bem-vindo!'}
                </Text>
                <Text style={styles.brand}>ECO CONTROL</Text>
              </View>
            </View>

            <TouchableOpacity style={styles.circleButton} onPress={() => setMenuAberto(true)}>
              <Feather name="menu" size={24} color="#FFFFFF" />
            </TouchableOpacity>
          </View>

          <View style={styles.topCardsRow}>
            <View style={styles.metaCard}>
              <View style={styles.metaHeader}>
                <Feather name="target" size={18} color="#9BFF81" />
                <Text style={styles.metaTitle}>Meta importante</Text>
              </View>

              <Text style={styles.metaSubtitle}>Economizar água</Text>

              <Text style={styles.metaMoney}>
                <Text style={styles.metaMoneyStrong}>R$100</Text>
                <Text style={styles.metaMoneySoft}> / R$250,00</Text>
              </Text>

              <View style={styles.progressTrack}>
                <View style={styles.progressFill} />
                <Text style={styles.progressText}>40%</Text>
              </View>

              <Text style={styles.metaProgressText}>40% da meta atingida</Text>

              <View style={styles.metaDateRow}>
                <Feather name="calendar" size={15} color="#B8C6BE" />
                <Text style={styles.metaDate}>Data limite: 31/05/2026</Text>
              </View>
            </View>

            <View style={styles.visualCard}>
              <MaterialCommunityIcons name="sprout" size={54} color="#A8FF8A" />
              <Text style={styles.visualText}>
                Pequenas atitudes geram grandes{'\n'}
                <Text style={styles.visualTextHighlight}>transformações.</Text>
              </Text>
            </View>
          </View>

          <Text style={styles.sectionTitle}>Resumo do seu consumo</Text>

          <View style={styles.chartModeRow}>
            {[
              { key: 'tipo', label: 'Tipo' },
              { key: 'dia', label: 'Dia' },
              { key: 'mes', label: 'Mês' },
              { key: 'todos', label: 'Todos' },
            ].map((item) => (
              <TouchableOpacity
                key={item.key}
                onPress={() => setTipoGrafico(item.key as any)}
                style={[
                  styles.chartModeButton,
                  tipoGrafico === item.key && styles.chartModeButtonActive,
                ]}
              >
                <Text
                  style={[
                    styles.chartModeText,
                    tipoGrafico === item.key && styles.chartModeTextActive,
                  ]}
                >
                  {item.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <View style={styles.chartCard}>
            <View style={styles.chartArea}>
              {chartData.map((item) => {
                const barHeight = maxValue > 0 ? (item.value / maxValue) * 95 : 0;

                return (
                  <View key={item.label} style={styles.barColumn}>
                    <Text style={styles.barValue}>
                      {item.value.toLocaleString('pt-BR', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </Text>

                    <View
                      style={[
                        styles.bar,
                        { height: barHeight, backgroundColor: item.color },
                      ]}
                    />

                    <Text style={styles.barLabel}>{item.label}</Text>
                  </View>
                );
              })}
            </View>
          </View>
        </ScrollView>

        <View style={styles.bottomNav}>
          <TouchableOpacity style={styles.navItemActive}>
            <Ionicons name="home" size={20} color="#7AF46C" />
            <Text style={styles.navTextActive}>Início</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.navItem}
            onPress={() => router.push('/consumo/analise-consumos')}
          >
            <Ionicons name="bar-chart-outline" size={20} color="#C7D6CE" />
            <Text style={styles.navText}>Consumo</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.navCenterButton}
            onPress={() => router.push('/consumo/registro-consumo')}
          >
            <Feather name="plus" size={26} color="#103221" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.navItem} onPress={() => router.push('/metas')}>
            <Feather name="target" size={20} color="#C7D6CE" />
            <Text style={styles.navText}>Metas</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.navItem} onPress={() => router.push('/documento')}>
            <MaterialCommunityIcons name="file-upload-outline" size={20} color="#C7D6CE" />
            <Text style={styles.navText}>Arquivo</Text>
          </TouchableOpacity>
        </View>

        <MenuLateral aberto={menuAberto} fechar={() => setMenuAberto(false)} />
      </LinearGradient>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: theme.colors.backgroundBottom },
  container: { flex: 1 },
  scrollContent: { paddingHorizontal: 18, paddingTop: 18, paddingBottom: 150 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 },
  headerLeft: { flexDirection: 'row', alignItems: 'center', flex: 1 },
  avatar: { width: 48, height: 48, borderRadius: 24, backgroundColor: 'rgba(120,255,140,0.08)', alignItems: 'center', justifyContent: 'center', marginRight: 10 },
  title: { fontSize: 20, fontWeight: 'bold', color: '#FFFFFF' },
  brand: { color: '#6BE36D', fontSize: 12, marginTop: 2 },
  circleButton: { width: 48, height: 48, borderRadius: 24, backgroundColor: 'rgba(255,255,255,0.05)', alignItems: 'center', justifyContent: 'center' },
  topCardsRow: { flexDirection: 'row', gap: 12, marginBottom: 24 },
  metaCard: { flex: 1.2, backgroundColor: 'rgba(7, 47, 40, 0.94)', borderRadius: 24, padding: 16 },
  metaHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 16 },
  metaTitle: { color: '#F4FFF4', fontSize: 14, fontWeight: '800', marginLeft: 8 },
  metaSubtitle: { color: '#E1ECE4', fontSize: 16, marginBottom: 14 },
  metaMoney: { marginBottom: 18 },
  metaMoneyStrong: { color: '#74F05E', fontSize: 20, fontWeight: '900' },
  metaMoneySoft: { color: '#E4ECE6', fontSize: 18, fontWeight: '700' },
  progressTrack: { height: 18, borderRadius: 999, backgroundColor: 'rgba(255,255,255,0.10)', overflow: 'hidden', marginBottom: 16, justifyContent: 'center' },
  progressFill: { width: '40%', height: '100%', backgroundColor: '#6EEB62', borderRadius: 999 },
  progressText: { position: 'absolute', right: 10, color: '#F7FFF6', fontSize: 13, fontWeight: '800' },
  metaProgressText: { color: '#74F05E', fontSize: 14, fontWeight: '800', marginBottom: 14 },
  metaDateRow: { flexDirection: 'row', alignItems: 'center' },
  metaDate: { color: '#B8C6BE', fontSize: 12, marginLeft: 8 },
  visualCard: { flex: 0.82, backgroundColor: 'rgba(7, 47, 40, 0.94)', borderRadius: 24, padding: 18, alignItems: 'center', justifyContent: 'space-around' },
  visualText: { color: '#F2FFF2', fontSize: 13, fontWeight: '700', textAlign: 'center' },
  visualTextHighlight: { color: '#7AF46C', fontWeight: '900' },
  sectionTitle: { color: '#FFFFFF', fontSize: 16, fontWeight: '900', marginBottom: 14 },
  chartModeRow: { flexDirection: 'row', gap: 8, marginBottom: 12 },
  chartModeButton: { paddingHorizontal: 14, paddingVertical: 9, borderRadius: 12, backgroundColor: 'rgba(255,255,255,0.06)' },
  chartModeButtonActive: { backgroundColor: '#7AF46C' },
  chartModeText: { color: '#E8F3EC', fontSize: 12, fontWeight: '800' },
  chartModeTextActive: { color: '#103221' },
  chartCard: { backgroundColor: 'rgba(7, 47, 40, 0.94)', borderRadius: 24, padding: 16, marginBottom: 24 },
  chartArea: { height: 150, flexDirection: 'row', alignItems: 'flex-end', justifyContent: 'space-around' },
  barColumn: { alignItems: 'center', justifyContent: 'flex-end' },
  barValue: { color: '#F0FFF0', fontSize: 14, fontWeight: '800', marginBottom: 8 },
  bar: { width: 36, borderTopLeftRadius: 8, borderTopRightRadius: 8 },
  barLabel: { color: '#E5F1E8', fontSize: 11, marginTop: 10 },
  bottomNav: { position: 'absolute', left: 18, right: 18, bottom: 14, height: 68, borderRadius: 24, backgroundColor: 'rgba(10, 38, 28, 0.98)', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-around' },
  navItem: { width: 56, alignItems: 'center', justifyContent: 'center' },
  navItemActive: { width: 56, alignItems: 'center', justifyContent: 'center' },
  navCenterButton: { width: 56, height: 56, borderRadius: 28, backgroundColor: '#6EE86A', alignItems: 'center', justifyContent: 'center', marginTop: -6 },
  navText: { color: '#C7D6CE', fontSize: 10, marginTop: 2 },
  navTextActive: { color: '#7AF46C', fontSize: 10, fontWeight: '800', marginTop: 2 },
});
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiFetch } from '../../services/api';
import React, { useState } from 'react';
import MenuLateral from '../../components/Menulateral';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  ScrollView,
  TextInput,
  Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Feather, Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import DateTimePicker from '@react-native-community/datetimepicker';
import { useRouter } from 'expo-router';
import { theme } from '../../constants/theme';

const tiposConsumo = [
  { label: 'Água', icon: 'water-outline', color: '#6EDBFF' },
  { label: 'Energia', icon: 'flash-outline', color: '#FFD84D' },
  { label: 'Gás', icon: 'flame-outline', color: '#FF7A59' },
  { label: 'Gasolina', icon: 'car-sport-outline', color: '#FF6464' },
] as const;

export default function RegistroConsumo() {
  const router = useRouter();
  const [menuAberto, setMenuAberto] = useState(false);
  const [tipo, setTipo] = useState('Água');
  const [valor, setValor] = useState('');
  const [data, setData] = useState('');
  const [abrirTipos, setAbrirTipos] = useState(false);
  const [mensagemSucesso, setMensagemSucesso] = useState(false);
  const [mostrarCalendario, setMostrarCalendario] = useState(false);
  const [dataSelecionada, setDataSelecionada] = useState(new Date());

  function selecionarTipo(novoTipo: string) {
    setTipo(novoTipo);
    setAbrirTipos(false);
  }

  function formatarData(dataValor: Date) {
    const dia = String(dataValor.getDate()).padStart(2, '0');
    const mes = String(dataValor.getMonth() + 1).padStart(2, '0');
    const ano = dataValor.getFullYear();
    return `${dia}/${mes}/${ano}`;
  }

  function formatarDataWebParaBr(valorData: string) {
    if (!valorData) return '';
    const [ano, mes, dia] = valorData.split('-');
    return `${dia}/${mes}/${ano}`;
  }
  function formatarMoeda(texto: string) {
  const numeros = texto.replace(/\D/g, '');

  if (!numeros) {
    return '';
  }

  const valorNumerico = Number(numeros) / 100;

  return valorNumerico.toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

  function formatarDataBrParaWeb(valorBr: string) {
    if (!valorBr || valorBr.length !== 10) return '';
    const [dia, mes, ano] = valorBr.split('/');
    return `${ano}-${mes}-${dia}`;
  }
  async function buscarIdUsuario() {
  const idDireto =
    await AsyncStorage.getItem('id_usuario') ||
    await AsyncStorage.getItem('usuario_id') ||
    await AsyncStorage.getItem('user_id');

  if (idDireto) return Number(idDireto);

  const usuarioSalvo = await AsyncStorage.getItem('usuario');

  if (usuarioSalvo) {
    const usuario = JSON.parse(usuarioSalvo);

    return Number(
      usuario.id_usuario ||
      usuario.usuario_id ||
      usuario.id ||
      usuario.user_id
    );
  }

  return null;
}
  async function registrarConsumo() {
  if (!tipo || !valor) {
    alert('Preencha o tipo e o valor');
    return;
  }

  try {
    const idUsuario = await buscarIdUsuario();

    if (!idUsuario) {
      alert('Usuário não encontrado. Faça login novamente.');
      return;
    }

    const valorNumerico = Number(
      valor.replace(/\./g, '').replace(',', '.')
    );

    await apiFetch('/consumo', {
      method: 'POST',
      body: JSON.stringify({
        tipo,
        valor: valorNumerico,
        data,
        id_usuario: Number(idUsuario),
        id_meta: null,
      }),
    });

    setMensagemSucesso(true);

    setTimeout(() => {
      setMensagemSucesso(false);
      setValor('');
      setData('');
      router.replace('/(tabs)/home');
    }, 1200);
  } catch (error: any) {
    console.log('ERRO COMPLETO:', error);

    alert(JSON.stringify(error?.data || error?.message || error, null, 2));
  }
}

  const tipoSelecionado =
    tiposConsumo.find((item) => item.label === tipo) || tiposConsumo[0];

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
          <View style={styles.header}>
            <View style={styles.headerLeft}>
              <View style={styles.logoCircle}>
                <MaterialCommunityIcons name="leaf" size={22} color="#8CFF8A" />
              </View>

              <View>
                <Text style={styles.headerBrand}>ECO CONTROL</Text>
                <Text style={styles.headerTitle}>Registro de consumos</Text>
              </View>
            </View>

            <TouchableOpacity
              style={styles.menuButton}
              onPress={() => setMenuAberto(true)}
            >
              <Feather name="menu" size={24} color="#FFFFFF" />
            </TouchableOpacity>
          </View>

          <View style={styles.mainCard}>
            <View style={styles.formHeaderCard}>
              <View style={styles.formHeaderIcon}>
                <Ionicons name="document-text-outline" size={30} color="#8CFF8A" />
              </View>

              <Text style={styles.formHeaderText}>
                Registre um{'\n'}
                <Text style={styles.formHeaderHighlight}>consumo:</Text>
              </Text>
            </View>

            <View style={styles.formCard}>
              <Text style={styles.label}>Tipo:</Text>

              <View style={styles.dropdownWrapper}>
                <TouchableOpacity
                  style={styles.dropdownButton}
                  activeOpacity={0.9}
                  onPress={() => setAbrirTipos(!abrirTipos)}
                >
                  <View style={styles.dropdownLeft}>
                    <Ionicons
                      name={tipoSelecionado.icon}
                      size={20}
                      color={tipoSelecionado.color}
                    />
                    <Text style={styles.dropdownText}>{tipo}</Text>
                  </View>

                  <Feather
                    name={abrirTipos ? 'chevron-up' : 'chevron-down'}
                    size={18}
                    color="#E7F2EA"
                  />
                </TouchableOpacity>

                {abrirTipos && (
                  <View style={styles.dropdownMenu}>
                    {tiposConsumo.map((item) => (
                      <TouchableOpacity
                        key={item.label}
                        style={styles.dropdownItem}
                        onPress={() => selecionarTipo(item.label)}
                      >
                        <Ionicons name={item.icon} size={19} color={item.color} />
                        <Text style={styles.dropdownItemText}>{item.label}</Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                )}
              </View>

              <Text style={styles.label}>Valor:</Text>
              <View style={styles.inputBox}>
                <Text style={styles.inputPrefix}>R$</Text>
                <TextInput
                  value={valor}
                  onChangeText={(texto) => setValor(formatarMoeda(texto))}
                  placeholder="0,00"
                  placeholderTextColor={theme.colors.placeholder}
                  keyboardType="numeric"
                  style={styles.input}
                />
              </View>

              <Text style={styles.label}>Data:</Text>

              {Platform.OS === 'web' ? (
              <View style={styles.inputBox}>
                <Ionicons
                  name="calendar-outline"
                  size={20}
                  color="#8CFF8A"
                  style={styles.inputIcon}
                />

                <input
                  type="date"
                  max={new Date().toISOString().split('T')[0]}
                  value={formatarDataBrParaWeb(data)}
                  onChange={(e) => {
                    setData(formatarDataWebParaBr(e.target.value));
                  }}
                  style={{
                    flex: 1,
                    background: 'transparent',
                    border: 'none',
                    outline: 'none',
                    color: '#F3FFF2',
                    fontSize: '15px',
                  }}
                />
              </View>
            ) : (
                <TouchableOpacity
                  style={styles.inputBox}
                  activeOpacity={0.9}
                  onPress={() => setMostrarCalendario(true)}
                >
                  <Ionicons
                    name="calendar-outline"
                    size={20}
                    color="#8CFF8A"
                    style={styles.inputIcon}
                  />

                  <Text
                    style={[
                      styles.input,
                      { color: data ? '#F3FFF2' : theme.colors.placeholder },
                    ]}
                  >
                    {data || 'Selecione uma data'}
                  </Text>

                  <Feather name="calendar" size={18} color="#E7F2EA" />
                </TouchableOpacity>
              )}
            </View>

            <TouchableOpacity style={styles.registerButton} onPress={registrarConsumo}>
              <Text style={styles.registerButtonText}>Registrar</Text>
            </TouchableOpacity>

            {mensagemSucesso && (
              <View style={styles.successCard}>
                <View style={styles.successLeft}>
                  <View style={styles.successIconCircle}>
                    <Feather name="check" size={20} color="#8CFF8A" />
                  </View>

                  <Text style={styles.successText}>
                    Consumo cadastrado{'\n'}com sucesso!
                  </Text>
                </View>

                <MaterialCommunityIcons
                  name="leaf"
                  size={30}
                  color="rgba(140,255,138,0.20)"
                />
              </View>
            )}
          </View>
        </ScrollView>

        {mostrarCalendario && Platform.OS !== 'web' && (
          <DateTimePicker
            value={dataSelecionada}
            mode="date"
            display="default"
            maximumDate={new Date()}
            onChange={(event, selectedDate) => {
              setMostrarCalendario(false);

              if (selectedDate) {
                setDataSelecionada(selectedDate);
                setData(formatarData(selectedDate));
              }
            }}
          />
        )}

          <View style={styles.bottomNav}>
          <TouchableOpacity
            style={styles.navItem}
            onPress={() => router.push('/(tabs)/home')}
          >
            <Ionicons name="home-outline" size={20} color="#C7D6CE" />
            <Text style={styles.navText}>Início</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.navItem}
            onPress={() => router.push('/consumo/analise-consumos')}
          >
            <Ionicons name="bar-chart-outline" size={20} color="#C7D6CE" />
            <Text style={styles.navText}>Consumo</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.navCenterButton}>
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
            </LinearGradient>

      <MenuLateral
        aberto={menuAberto}
        fechar={() => setMenuAberto(false)}
      />
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

  scrollContent: {
    paddingHorizontal: 16,
    paddingTop: 14,
    paddingBottom: 130,
  },

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

  headerTitle: {
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

  mainCard: {
    backgroundColor: 'rgba(7, 47, 40, 0.94)',
    borderRadius: 24,
    borderWidth: 1,
    borderColor: 'rgba(120, 255, 140, 0.12)',
    padding: 14,
  },

  formHeaderCard: {
    backgroundColor: 'rgba(12, 58, 50, 0.92)',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(120,255,140,0.10)',
    paddingVertical: 14,
    paddingHorizontal: 14,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 14,
  },

  formHeaderIcon: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: 'rgba(120,255,140,0.08)',
    borderWidth: 1,
    borderColor: 'rgba(120,255,140,0.14)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },

  formHeaderText: {
    color: '#F5FFF4',
    fontSize: 18,
    fontWeight: '800',
    lineHeight: 24,
  },

  formHeaderHighlight: {
    color: '#7AF46C',
  },

  formCard: {
    backgroundColor: 'rgba(5, 53, 49, 0.76)',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(120,255,140,0.10)',
    padding: 14,
    marginBottom: 14,
  },

  label: {
    color: '#F1FFF0',
    fontSize: 15,
    fontWeight: '800',
    marginBottom: 8,
    marginTop: 2,
  },

  dropdownWrapper: {
    marginBottom: 14,
    position: 'relative',
    zIndex: 10,
  },

  dropdownButton: {
    height: 54,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(120,255,140,0.22)',
    backgroundColor: 'rgba(4, 39, 37, 0.92)',
    paddingHorizontal: 14,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },

  dropdownLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },

  dropdownText: {
    color: '#F1FFF0',
    fontSize: 15,
    marginLeft: 10,
    fontWeight: '600',
  },

  dropdownMenu: {
    position: 'absolute',
    top: 60,
    left: 0,
    right: 0,
    borderRadius: 16,
    backgroundColor: 'rgba(4, 39, 37, 0.98)',
    borderWidth: 1,
    borderColor: 'rgba(120,255,140,0.22)',
    overflow: 'hidden',
  },

  dropdownItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 14,
    paddingVertical: 13,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.06)',
  },

  dropdownItemText: {
    color: '#F1FFF0',
    fontSize: 15,
    marginLeft: 10,
  },

  inputBox: {
    height: 54,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(120,255,140,0.22)',
    backgroundColor: 'rgba(4, 39, 37, 0.92)',
    paddingHorizontal: 14,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 14,
  },

  inputPrefix: {
    color: '#7AF46C',
    fontSize: 17,
    fontWeight: '900',
    marginRight: 12,
  },

  inputIcon: {
    marginRight: 10,
  },

  input: {
    flex: 1,
    color: '#F3FFF2',
    fontSize: 15,
  },

  registerButton: {
    height: 60,
    borderRadius: 50,
    backgroundColor: '#7AF46C',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 10,
    shadowColor: '#7AF46C',
    shadowOpacity: 0.22,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 5 },
    elevation: 8,
  },

  registerButtonText: {
    color: '#123220',
    fontSize: 20,
    fontWeight: '900',
  },

  successCard: {
    height: 78,
    borderRadius: 20,
    backgroundColor: 'rgba(8, 42, 38, 0.96)',
    borderWidth: 1,
    borderColor: 'rgba(120,255,140,0.10)',
    paddingHorizontal: 14,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },

  successLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },

  successIconCircle: {
    width: 42,
    height: 42,
    borderRadius: 21,
    borderWidth: 1,
    borderColor: 'rgba(120,255,140,0.18)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },

  successText: {
    color: '#F1FFF0',
    fontSize: 13,
    lineHeight: 18,
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
  width: 58,
  height: 58,
  borderRadius: 29,
  backgroundColor: '#7AF46C',
  alignItems: 'center',
  justifyContent: 'center',
  marginTop: -4,
  shadowColor: '#7AF46C',
  shadowOpacity: 1.20,
  shadowRadius: 10,
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
import React, { useEffect, useMemo, useState } from 'react'
import { ArrowUpRight, Building2, CreditCard, Landmark, Smartphone, Wallet } from 'lucide-react'
import { paymentAPI } from '../utils/api'
import { useAuth } from '../context/AuthContext'
import { formatCurrency, formatDate } from '../utils/formatting'

const METHOD_META = {
  mpesa: {
    label: 'M-Pesa',
    icon: Smartphone,
    provider: 'Safaricom M-Pesa',
    accent: 'text-success-400 border-success-500/30 bg-success-500/10',
    helper: 'Use this for wallet top-ups or withdrawals to an M-Pesa number.',
  },
  bank: {
    label: 'Bank Transfer',
    icon: Landmark,
    provider: 'Commercial bank',
    accent: 'text-primary-400 border-primary-500/30 bg-primary-500/10',
    helper: 'Use this for EFT/RTGS funding or bank-account withdrawals.',
  },
  card: {
    label: 'Card',
    icon: CreditCard,
    provider: 'Visa / Mastercard',
    accent: 'text-warning-400 border-warning-500/30 bg-warning-500/10',
    helper: 'Card remains available for deposits only.',
  },
  sacco: {
    label: 'SACCO / Microfinance',
    icon: Building2,
    provider: 'SACCO',
    accent: 'text-fuchsia-400 border-fuchsia-500/30 bg-fuchsia-500/10',
    helper: 'Useful for cooperative savings and local institution funding.',
  },
}

export const Deposit = () => {
  const { user, updateUser } = useAuth()
  const [activeFlow, setActiveFlow] = useState('deposit')
  const [selectedMethod, setSelectedMethod] = useState('mpesa')
  const [formData, setFormData] = useState({
    amount_kes: 1000,
    phone_number: '',
    institution_name: '',
    account_reference: '',
    notes: '',
  })
  const [history, setHistory] = useState([])
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [providerReference, setProviderReference] = useState('')

  const availableMethods = useMemo(
    () =>
      activeFlow === 'withdrawal'
        ? ['mpesa', 'bank']
        : Object.keys(METHOD_META),
    [activeFlow]
  )

  const loadTransactions = async () => {
    try {
      const { data } = await paymentAPI.getDeposits()
      setHistory(data.deposits || [])
    } catch {
      // Keep page usable even if history is unavailable.
    }
  }

  useEffect(() => {
    loadTransactions()
  }, [])

  useEffect(() => {
    if (!availableMethods.includes(selectedMethod)) {
      setSelectedMethod(availableMethods[0])
    }
  }, [availableMethods, selectedMethod])

  const handleChange = (event) => {
    const { name, value } = event.target
    setMessage('')
    setFormData((previous) => ({
      ...previous,
      [name]: name === 'amount_kes' ? Number(value) : value,
    }))
  }

  const resetForm = () => {
    setFormData({
      amount_kes: 1000,
      phone_number: '',
      institution_name: '',
      account_reference: '',
      notes: '',
    })
  }

  const handleDeposit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setMessage('')

    try {
      const payload = {
        method: selectedMethod,
        amount_kes: formData.amount_kes,
        phone_number: formData.phone_number || undefined,
        institution_name: formData.institution_name || undefined,
        account_reference: formData.account_reference || undefined,
        notes: formData.notes || undefined,
      }

      const { data } = await paymentAPI.createDeposit(payload)
      if (data.status === 'completed') {
        updateUser({
          ...user,
          balance: (user?.balance || 0) + Number(data.amount_kes),
        })
        setMessage(`${METHOD_META[selectedMethod].label} deposit completed. Ref: ${data.reference}`)
      } else {
        setMessage(`${METHOD_META[selectedMethod].label} deposit request created. Status: ${data.status}. Complete the provider step, then confirm below.`)
      }
      resetForm()
      await loadTransactions()
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Deposit request failed')
    } finally {
      setLoading(false)
    }
  }

  const handleWithdrawal = async (event) => {
    event.preventDefault()
    setLoading(true)
    setMessage('')

    try {
      const payload = {
        method: selectedMethod,
        amount_kes: formData.amount_kes,
        phone_number: formData.phone_number || undefined,
        institution_name: formData.institution_name || undefined,
        account_reference: formData.account_reference || undefined,
        notes: formData.notes || undefined,
      }

      const { data } = await paymentAPI.createWithdrawal(payload)
      updateUser({
        ...user,
        balance: Math.max((user?.balance || 0) - Number(data.amount_kes), 0),
      })
      setMessage(`${METHOD_META[selectedMethod].label} withdrawal requested. Ref: ${data.reference}. The amount has been reserved from your wallet.`)
      resetForm()
      await loadTransactions()
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Withdrawal request failed')
    } finally {
      setLoading(false)
    }
  }

  const selectedMeta = METHOD_META[selectedMethod]

  const handleConfirmTransaction = async (transactionId) => {
    try {
      const transaction = history.find((item) => item.id === transactionId)
      const { data } = await paymentAPI.confirmDeposit(transactionId, {
        provider_reference: providerReference || undefined,
      })

      if (transaction?.transaction_type === 'deposit') {
        updateUser({
          ...user,
          balance: (user?.balance || 0) + Number(data.amount_kes),
        })
        setMessage(`Deposit ${data.reference} confirmed and credited.`)
      } else {
        setMessage(`Withdrawal ${data.reference} confirmed for payout.`)
      }

      setProviderReference('')
      await loadTransactions()
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Unable to confirm transaction')
    }
  }

  return (
    <div className="min-h-screen bg-dark-950 pt-8 pb-12">
      <div className="mx-auto max-w-7xl px-4 sm:px-5">
        <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h1 className="text-2xl sm:text-3xl font-display font-bold text-dark-100">Wallet Center</h1>
            <p className="mt-2 text-dark-400">
              Deposit simulated funds or withdraw trading profits to your M-Pesa wallet or bank account.
            </p>
          </div>

          <div className="rounded-2xl border border-dark-700 bg-dark-800 px-5 py-4">
            <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Current balance</p>
            <p className="mt-1 flex items-center gap-2 text-2xl font-semibold text-primary-300">
              <Wallet className="h-5 w-5" />
              {formatCurrency(user?.balance || 0, 0)}
            </p>
          </div>
        </div>

        <div className="mb-6 grid grid-cols-2 gap-3 rounded-2xl border border-dark-700 bg-dark-800 p-2">
          <button
            onClick={() => setActiveFlow('deposit')}
            className={`rounded-xl px-4 py-3 text-sm font-semibold ${activeFlow === 'deposit' ? 'bg-primary-600 text-white' : 'text-dark-300'}`}
          >
            Deposit
          </button>
          <button
            onClick={() => setActiveFlow('withdrawal')}
            className={`rounded-xl px-4 py-3 text-sm font-semibold ${activeFlow === 'withdrawal' ? 'bg-success-600 text-white' : 'text-dark-300'}`}
          >
            Withdraw
          </button>
        </div>

        <div className="grid gap-6 xl:grid-cols-[340px_minmax(0,1fr)]">
          <aside className="rounded-2xl border border-dark-700 bg-dark-800 p-4">
            <h2 className="mb-4 text-sm font-semibold uppercase tracking-[0.16em] text-dark-400">
              {activeFlow === 'deposit' ? 'Funding Methods' : 'Withdrawal Methods'}
            </h2>
            <div className="space-y-3">
              {availableMethods.map((key) => {
                const meta = METHOD_META[key]
                const Icon = meta.icon
                const active = key === selectedMethod
                return (
                  <button
                    key={key}
                    onClick={() => setSelectedMethod(key)}
                    className={`w-full rounded-xl border px-4 py-4 text-left transition ${
                      active ? meta.accent : 'border-dark-700 bg-dark-900 hover:border-dark-600'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <Icon className="mt-0.5 h-5 w-5" />
                      <div>
                        <p className="font-semibold text-dark-100">{meta.label}</p>
                        <p className="mt-1 text-xs text-dark-400">{meta.provider}</p>
                      </div>
                    </div>
                  </button>
                )
              })}
            </div>
          </aside>

          <div className="space-y-6">
            <section className="rounded-2xl border border-dark-700 bg-dark-800 p-6">
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-dark-100">
                  {selectedMeta.label} {activeFlow === 'deposit' ? 'Deposit' : 'Withdrawal'}
                </h2>
                <p className="mt-1 text-sm text-dark-400">{selectedMeta.helper}</p>
              </div>

              <form onSubmit={activeFlow === 'deposit' ? handleDeposit : handleWithdrawal} className="space-y-4">
                {message && (
                  <div className={`rounded-xl border px-4 py-3 text-sm ${
                    message.toLowerCase().includes('completed') || message.toLowerCase().includes('confirmed')
                      ? 'border-success-500/30 bg-success-500/10 text-success-300'
                      : 'border-red-500/30 bg-red-500/10 text-red-300'
                  }`}>
                    {message}
                  </div>
                )}

                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <label className="mb-2 block text-sm font-medium text-dark-300">Amount (KES)</label>
                    <input
                      name="amount_kes"
                      type="number"
                      min="50"
                      step="50"
                      value={formData.amount_kes}
                      onChange={handleChange}
                      className="input-field"
                      required
                    />
                  </div>

                  <div>
                    <label className="mb-2 block text-sm font-medium text-dark-300">Institution</label>
                    <input
                      name="institution_name"
                      type="text"
                      value={formData.institution_name}
                      onChange={handleChange}
                      placeholder={selectedMeta.provider}
                      className="input-field"
                    />
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <label className="mb-2 block text-sm font-medium text-dark-300">
                      {selectedMethod === 'mpesa' ? 'M-Pesa Number' : 'Phone / Contact'}
                    </label>
                    <input
                      name="phone_number"
                      type="text"
                      value={formData.phone_number}
                      onChange={handleChange}
                      placeholder={selectedMethod === 'mpesa' ? '2547XXXXXXXX' : 'Optional contact'}
                      className="input-field"
                    />
                  </div>

                  <div>
                    <label className="mb-2 block text-sm font-medium text-dark-300">Reference</label>
                    <input
                      name="account_reference"
                      type="text"
                      value={formData.account_reference}
                      onChange={handleChange}
                      placeholder={activeFlow === 'deposit' ? 'Account / card / receipt reference' : 'Bank account / payout reference'}
                      className="input-field"
                    />
                  </div>
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium text-dark-300">Notes</label>
                  <textarea
                    name="notes"
                    value={formData.notes}
                    onChange={handleChange}
                    rows={3}
                    placeholder={`Optional ${activeFlow} notes`}
                    className="input-field"
                  />
                </div>

                <div className="rounded-2xl border border-dark-700 bg-dark-900 px-4 py-4 text-sm text-dark-400">
                  {activeFlow === 'deposit'
                    ? 'Deposits can complete instantly or follow a provider-style confirmation flow depending on the method and environment.'
                    : 'Withdrawals reserve the requested amount from the wallet immediately, then move through a provider-style payout confirmation flow.'}
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className={`w-full ${activeFlow === 'deposit' ? 'btn-primary' : 'btn-success'}`}
                >
                  {loading
                    ? activeFlow === 'deposit'
                      ? 'Processing deposit...'
                      : 'Processing withdrawal...'
                    : activeFlow === 'deposit'
                      ? `Deposit via ${selectedMeta.label}`
                      : `Withdraw to ${selectedMeta.label}`}
                </button>
              </form>
            </section>

            <section className="rounded-2xl border border-dark-700 bg-dark-800 p-6">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-xl font-semibold text-dark-100">Wallet History</h2>
                <div className="rounded-full border border-dark-700 bg-dark-900 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-dark-400">
                  Deposits & Withdrawals
                </div>
              </div>

              <div className="space-y-3">
                {history.length === 0 && (
                  <div className="rounded-xl border border-dark-700 bg-dark-900 px-4 py-6 text-sm text-dark-400">
                    No wallet transactions yet. Your funding and withdrawal activity will appear here.
                  </div>
                )}

                {history.map((item) => {
                  const meta = METHOD_META[item.method] || METHOD_META.bank
                  const isWithdrawal = item.transaction_type === 'withdrawal'
                  return (
                    <div key={item.id} className="rounded-xl border border-dark-700 bg-dark-900 px-4 py-4">
                      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                        <div className="flex items-start gap-3">
                          <div className={`mt-1 rounded-full p-2 ${isWithdrawal ? 'bg-success-500/10 text-success-400' : 'bg-primary-500/10 text-primary-400'}`}>
                            {isWithdrawal ? <ArrowUpRight className="h-4 w-4" /> : <Wallet className="h-4 w-4" />}
                          </div>
                          <div>
                            <p className="font-semibold text-dark-100">
                              {isWithdrawal ? 'Withdrawal' : 'Deposit'} · {meta.label} · {formatCurrency(item.amount_kes, 0)}
                            </p>
                            <p className="mt-1 text-sm text-dark-400">
                              {item.reference} · {item.provider || meta.provider}
                            </p>
                          </div>
                        </div>

                        <div className="text-right">
                          <p className={`badge ${item.status === 'completed' ? 'badge-success' : 'badge-warning'}`}>{item.status}</p>
                          <p className="mt-2 text-sm text-dark-400">{formatDate(item.created_at)}</p>
                        </div>
                      </div>

                      {(item.status === 'pending' || item.status === 'action_required') && (
                        <div className="mt-4 rounded-xl border border-dark-700 bg-dark-800/80 p-4">
                          <p className="text-sm text-dark-300">
                            {item.checkout_url
                              ? `Complete the hosted ${item.method} step, then confirm here.`
                              : isWithdrawal
                                ? 'Confirm once the payout instruction has been acknowledged by the provider.'
                                : 'Enter the payment/provider reference and confirm once the transfer is complete.'}
                          </p>
                          {item.checkout_url && (
                            <a
                              href={item.checkout_url}
                              target="_blank"
                              rel="noreferrer"
                              className="mt-3 inline-flex rounded-lg bg-primary-600 px-3 py-2 text-sm font-semibold text-white hover:bg-primary-700"
                            >
                              Open Checkout
                            </a>
                          )}
                          <div className="mt-3 flex flex-col gap-3 md:flex-row">
                            <input
                              type="text"
                              value={providerReference}
                              onChange={(event) => setProviderReference(event.target.value)}
                              placeholder={isWithdrawal ? 'Payout / provider reference' : 'Provider / M-Pesa code'}
                              className="input-field"
                            />
                            <button onClick={() => handleConfirmTransaction(item.id)} className="btn-primary md:w-auto">
                              Confirm {isWithdrawal ? 'Withdrawal' : 'Deposit'}
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  )
}

import React, {useEffect, useState} from 'react'
import { useParams } from 'react-router-dom'

export default function Detail(){
  const { id } = useParams()
  const [doc, setDoc] = useState(null)

  useEffect(()=>{
    fetch(`/documentos/${id}`)
      .then(r=>r.json())
      .then(setDoc)
  },[id])

  if(!doc) return <div>Carregando...</div>

  const confirmar = () => {
    fetch(`/documentos/${id}/confirmar?usuario=system`, {method: 'POST'})
      .then(()=>{
        alert('Marcado como FEITO')
        // refetch
        fetch(`/documentos/${id}`).then(r=>r.json()).then(setDoc)
      })
  }

  const abrirEmailOriginal = async () => {
    const r = await fetch(`/documentos/${id}/email-original`)
    const data = await r.json()
    if (data.link) window.open(data.link, '_blank')
    else alert('Link não disponível')
  }

  return (
    <div className="container">
      <h1>Documento {doc.numero_documento || doc.id}</h1>
      <div className="card">
        <p><strong>Tipo:</strong> {doc.tipo}</p>
        <p><strong>Fornecedor:</strong> {doc.fornecedor}</p>
        <p><strong>CNPJ:</strong> {doc.cnpj}</p>
        <p><strong>Valor:</strong> {doc.valor}</p>
        <p><strong>Status:</strong> {doc.status}</p>
        <p><strong>Confirmado em:</strong> {doc.confirmado_em || '-'}</p>
        <button onClick={confirmar}>Marcar como FEITO</button>
        <button onClick={abrirEmailOriginal} style={{marginLeft: '8px'}}>Abrir e-mail original</button>
      </div>

      <div className="card">
        <h3>Preview</h3>
        {doc.anexos && doc.anexos[0] && doc.anexos[0].preview_imagem && (
          <img src={`data:image/png;base64,${doc.anexos[0].preview_imagem}`} alt="preview" style={{maxWidth: '800px'}} />
        )}
      </div>

      <div className="card">
        <h3>Histórico</h3>
        {doc.historicos && doc.historicos.length > 0 ? (
          <ul>
            {doc.historicos.map(h => (
              <li key={h.id}>{new Date(h.data_hora).toLocaleString()} - {h.evento} {h.usuario ? `by ${h.usuario}` : ''}</li>
            ))}
          </ul>
        ) : (
          <p>Sem histórico</p>
        )}
      </div>

    </div>
  )
}
